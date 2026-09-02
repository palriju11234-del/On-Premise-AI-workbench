"""
Document processing service — Phase 3 Document Intelligence.

Orchestrates the full document pipeline:
  file validation → type detection → text extraction → OCR fallback
  → security classification → local storage → structured result.

Wraps the existing ``document.parser`` and ``document.ocr`` modules
without modifying them.
"""

import io
import json
import logging
import mimetypes
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from backend.config import get_settings
from backend.exceptions import DocumentProcessingError
from backend.schemas.document import (
    DocumentType,
    DocumentMetadata,
    DocumentResult,
    DocumentListItem,
    PageContent,
)
from backend.services.security import SecurityService

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Threshold: if PyMuPDF extracts fewer characters than this per page
# on average, the document is likely scanned and OCR is needed.
OCR_TEXT_THRESHOLD = 100


def _tesseract_available() -> bool:
    """Check if Tesseract OCR is installed and reachable."""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


class DocumentService:
    """Core document processing pipeline."""

    def __init__(self):
        settings = get_settings()
        self._upload_dir = settings.upload_dir
        self._registry_file = settings.project_root / "backend" / "data" / "documents.json"
        self._security = SecurityService()
        self._ocr_available = _tesseract_available()

        # Ensure directories and registry exist
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        self._registry_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._registry_file.exists():
            self._registry_file.write_text("[]", encoding="utf-8")

        if self._ocr_available:
            logger.info("Tesseract OCR is available")
        else:
            logger.warning(
                "Tesseract OCR is NOT installed — OCR fallback disabled. "
                "Image-only documents will have empty text."
            )

    # ── Public API ───────────────────────────────────────────────────

    async def process_document(
        self,
        filename: str,
        file_content: bytes,
    ) -> DocumentResult:
        """
        Full processing pipeline for an uploaded document.

        1. Validate file
        2. Save to local storage
        3. Detect document type
        4. Extract text (PyMuPDF for PDF, OCR for images)
        5. OCR fallback for scanned PDFs
        6. Security classification
        7. Register in document store
        8. Return structured result
        """
        # 1. Validate
        self._validate_file(filename, file_content)

        # 2. Generate ID and save
        document_id = str(uuid.uuid4())
        ext = Path(filename).suffix.lower()
        stored_filename = f"{document_id}{ext}"
        stored_path = self._upload_dir / stored_filename
        stored_path.write_bytes(file_content)
        logger.info(
            "Saved document: id=%s filename=%s size=%d",
            document_id, filename, len(file_content),
        )

        try:
            # 3. Detect type
            doc_type = self._detect_type(ext, file_content)

            # 4 & 5. Extract text (with OCR fallback)
            pages, ocr_used = self._extract(stored_path, doc_type)

            # Full text
            extracted_text = "\n\n".join(p.text for p in pages)

            # 6. Security classification
            classification = self._security.classify(
                text=extracted_text[:5000],  # Classify on first 5 KB
                filename=filename,
            )

            # 7. Build metadata
            metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                document_type=doc_type,
                page_count=len(pages),
                ocr_used=ocr_used,
                classification=classification.classification.value,
                file_size_bytes=len(file_content),
            )

            result = DocumentResult(
                metadata=metadata,
                extracted_text=extracted_text,
                pages=pages,
                classification_score=classification.score,
                classification_keywords=classification.keywords_matched,
            )

            # 8. Register
            self._register_document(metadata)

            logger.info(
                "Processed document: id=%s type=%s pages=%d ocr=%s class=%s",
                document_id, doc_type.value, len(pages),
                ocr_used, classification.classification.value,
            )
            return result

        except DocumentProcessingError:
            # Clean up saved file on processing failure
            stored_path.unlink(missing_ok=True)
            raise
        except Exception as exc:
            stored_path.unlink(missing_ok=True)
            logger.exception("Unexpected error processing %s", filename)
            raise DocumentProcessingError(
                f"Failed to process document '{filename}': {exc}"
            )

    def list_documents(self) -> list[DocumentListItem]:
        """Return all registered documents."""
        registry = self._load_registry()
        return [
            DocumentListItem(
                document_id=doc["document_id"],
                filename=doc["filename"],
                document_type=DocumentType(doc["document_type"]),
                page_count=doc["page_count"],
                ocr_used=doc["ocr_used"],
                classification=doc["classification"],
                file_size_bytes=doc["file_size_bytes"],
                upload_timestamp=doc["upload_timestamp"],
            )
            for doc in registry
        ]

    def get_document(self, document_id: str) -> DocumentListItem | None:
        """Return metadata for a single document by ID."""
        registry = self._load_registry()
        for doc in registry:
            if doc["document_id"] == document_id:
                return DocumentListItem(
                    document_id=doc["document_id"],
                    filename=doc["filename"],
                    document_type=DocumentType(doc["document_type"]),
                    page_count=doc["page_count"],
                    ocr_used=doc["ocr_used"],
                    classification=doc["classification"],
                    file_size_bytes=doc["file_size_bytes"],
                    upload_timestamp=doc["upload_timestamp"],
                )
        return None

    # ── Validation ───────────────────────────────────────────────────

    def _validate_file(self, filename: str, content: bytes) -> None:
        """Validate file extension, MIME type, and size."""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise DocumentProcessingError(
                f"Unsupported file type '{ext}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        # MIME check
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type and mime_type not in ALLOWED_MIME_TYPES:
            raise DocumentProcessingError(
                f"MIME type '{mime_type}' is not allowed."
            )

        # Size check
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise DocumentProcessingError(
                f"File size ({len(content) / (1024*1024):.1f} MB) exceeds "
                f"maximum allowed size ({MAX_FILE_SIZE_MB} MB)."
            )

        if len(content) == 0:
            raise DocumentProcessingError("File is empty.")

    # ── Type Detection ───────────────────────────────────────────────

    def _detect_type(self, ext: str, content: bytes) -> DocumentType:
        """Detect whether a document is a PDF, scanned PDF, or image."""
        if ext in {".png", ".jpg", ".jpeg"}:
            return DocumentType.IMAGE

        if ext == ".pdf":
            # Check if PDF has extractable text
            try:
                doc = fitz.open(stream=content, filetype="pdf")
                total_text = sum(
                    len(page.get_text().strip()) for page in doc
                )
                avg_text = total_text / max(len(doc), 1)
                doc.close()

                if avg_text < OCR_TEXT_THRESHOLD:
                    return DocumentType.SCANNED_PDF
                return DocumentType.PDF
            except Exception:
                return DocumentType.UNKNOWN

        return DocumentType.UNKNOWN

    # ── Text Extraction ──────────────────────────────────────────────

    def _extract(
        self, file_path: Path, doc_type: DocumentType
    ) -> tuple[list[PageContent], bool]:
        """
        Extract text from the document.

        Returns (pages, ocr_used).
        Calls existing document.parser and document.ocr modules.
        """
        if doc_type == DocumentType.PDF:
            return self._extract_pdf_text(file_path), False

        elif doc_type == DocumentType.SCANNED_PDF:
            if self._ocr_available:
                return self._extract_pdf_ocr(file_path), True
            else:
                logger.warning(
                    "Scanned PDF detected but OCR unavailable: %s", file_path
                )
                # Fall back to whatever text PyMuPDF can get
                return self._extract_pdf_text(file_path), False

        elif doc_type == DocumentType.IMAGE:
            if self._ocr_available:
                return self._extract_image_ocr(file_path), True
            else:
                logger.warning(
                    "Image detected but OCR unavailable: %s", file_path
                )
                return [PageContent(page=1, text="[OCR unavailable]")], False

        else:
            raise DocumentProcessingError(
                f"Cannot extract text from type: {doc_type.value}"
            )

    def _extract_pdf_text(self, file_path: Path) -> list[PageContent]:
        """Extract text from PDF using the existing document.parser module."""
        # Import and call existing module (no modifications)
        from document.parser import extract_pdf_text
        raw_pages = extract_pdf_text(str(file_path))
        return [
            PageContent(page=p["page"], text=p["text"])
            for p in raw_pages
        ]

    def _extract_pdf_ocr(self, file_path: Path) -> list[PageContent]:
        """OCR a scanned PDF using the existing document.ocr module."""
        from document.ocr import ocr_pdf
        raw_pages = ocr_pdf(str(file_path))
        return [
            PageContent(page=p["page"], text=p["text"])
            for p in raw_pages
        ]

    def _extract_image_ocr(self, file_path: Path) -> list[PageContent]:
        """OCR a single image file using Pillow + Tesseract."""
        import pytesseract

        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return [PageContent(page=1, text=text)]

    # ── Registry ─────────────────────────────────────────────────────

    def _load_registry(self) -> list[dict]:
        """Load the document registry from disk."""
        try:
            return json.loads(self._registry_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _register_document(self, metadata: DocumentMetadata) -> None:
        """Append document metadata to the local registry."""
        registry = self._load_registry()
        registry.append(metadata.model_dump(mode="json"))
        self._registry_file.write_text(
            json.dumps(registry, indent=2, default=str),
            encoding="utf-8",
        )
