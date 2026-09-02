from typing import List, Dict, Any
from sovereign_ai.schemas.security import UserRole
from sovereign_ai.schemas.rag import (
    IngestDocumentRequest,
    IngestDocumentResponse,
    QueryResponse,
)
from sovereign_ai.rag.retriever import SovereignRetriever

# Local in-memory vector/index store
INDEX_STORE: List[Dict[str, Any]] = []


class RAGService:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 120, overlap: int = 20) -> List[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
            i += max(1, chunk_size - overlap)
        return chunks if chunks else [text]

    @classmethod
    def ingest_document(cls, req: IngestDocumentRequest) -> IngestDocumentResponse:
        chunks = cls.chunk_text(req.text)
        for idx, chunk_text in enumerate(chunks):
            chunk_entry = {
                "chunk_id": f"{req.document_id}_chunk_{idx}",
                "document_id": req.document_id,
                "filename": req.filename,
                "text": chunk_text,
                "classification": req.classification,
                "metadata": req.metadata or {},
            }
            INDEX_STORE.append(chunk_entry)

        return IngestDocumentResponse(
            status="indexed",
            document_id=req.document_id,
            chunks_indexed=len(chunks),
            classification=req.classification,
        )

    @classmethod
    def retrieve(cls, query: str, user_role: UserRole, top_k: int = 3) -> QueryResponse:
        return SovereignRetriever.retrieve(
            query=query,
            user_role=user_role,
            index_store=INDEX_STORE,
            top_k=top_k,
        )