import io
import hashlib
from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from pypdf import PdfReader

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/process")
async def process_document(
    file: UploadFile = File(...),
    x_role_clearance: str = Header("ENGINEER")
):
    try:
        contents = await file.read()
        file_sha = hashlib.sha256(contents).hexdigest()
        extracted_text = ""

        # Check file extension and extract text
        if file.filename.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(contents))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        else:
            # Fallback for plain text, csv, logs
            extracted_text = contents.decode("utf-8", errors="ignore")

        if not extracted_text.strip():
            extracted_text = "No readable text could be extracted from this document."

        return {
            "filename": file.filename,
            "bytes": len(contents),
            "sha256": file_sha,
            "text": extracted_text.strip(),
            "text_preview": extracted_text[:400].strip(),
            "status": "PROCESSED"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")