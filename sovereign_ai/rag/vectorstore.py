import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

import chromadb
from sentence_transformers import SentenceTransformer

from sovereign_ai.core.config import DATA_DIR
from sovereign_ai.schemas.security import DataClassification
from sovereign_ai.schemas.rag import RetrievedChunk


class LocalVectorStore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LocalVectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_dir: Optional[Path] = None):
        if self._initialized:
            return

        self.db_path = Path(db_dir) if db_dir else (DATA_DIR / "vector_db")
        self.db_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.collection = self.client.get_or_create_collection(
            name="enterprise_knowledge",
            metadata={"hnsw:space": "cosine"},
        )

        self.embedding_model = self._load_embedding_model()
        self._initialized = True

    def _load_embedding_model(self) -> SentenceTransformer:
        """Loads local cached model for strict air-gap/on-premise execution."""
        hf_snapshots = (
            Path.home()
            / ".cache"
            / "huggingface"
            / "hub"
            / "models--sentence-transformers--all-MiniLM-L6-v2"
            / "snapshots"
        )
        if hf_snapshots.exists():
            for snap in hf_snapshots.iterdir():
                if (snap / "model.safetensors").exists():
                    try:
                        from sentence_transformers.models import Transformer, Pooling, Normalize
                        t = Transformer(str(snap))
                        p = Pooling(384)
                        n = Normalize()
                        return SentenceTransformer(modules=[t, p, n])
                    except Exception:
                        try:
                            return SentenceTransformer(str(snap))
                        except Exception:
                            pass

        return SentenceTransformer("all-MiniLM-L6-v2")

        # Auto-seed knowledge if collection is currently empty
        if self.collection.count() == 0:
            self._seed_default_knowledge()

    def _seed_default_knowledge(self):
        """Seeds default documents from data/knowledge if available."""
        knowledge_dir = DATA_DIR / "knowledge"
        if not knowledge_dir.exists():
            return

        documents = []
        for file in knowledge_dir.glob("*.txt"):
            try:
                text = file.read_text(encoding="utf-8").strip()
                if text:
                    documents.append({
                        "document_id": file.stem,
                        "filename": file.name,
                        "text": text,
                        "classification": "INTERNAL",
                        "metadata": {"source": "default_seed"},
                    })
            except Exception:
                pass

        if documents:
            self.add_documents(documents)

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Ingests document chunks into ChromaDB with collision-safe upsert.
        """
        if not documents:
            return

        texts: List[str] = []
        ids: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for idx, d in enumerate(documents):
            text = (d.get("text") or "").strip()
            if not text:
                continue

            # Deterministic unique ID to prevent collisions during repeated ingestion
            chunk_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
            doc_id = (
                d.get("chunk_id")
                or d.get("id")
                or f"{d.get('document_id', 'doc')}_{idx}_{chunk_hash}"
            )

            classification = d.get("classification", "GENERAL")
            if hasattr(classification, "value"):
                classification = classification.value

            meta = {
                "document_id": str(d.get("document_id", "")),
                "filename": str(d.get("filename", "")),
                "classification": str(classification),
            }
            # Add any additional user metadata
            extra_meta = d.get("metadata") or {}
            for k, v in extra_meta.items():
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v

            ids.append(doc_id)
            texts.append(text)
            metadatas.append(meta)

        if not texts:
            return

        embeddings = self.embedding_model.encode(texts).tolist()

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
        allowed_clearances: Optional[Set[DataClassification]] = None,
    ) -> List[RetrievedChunk]:
        """
        Performs semantic vector retrieval filtered strictly by role-based clearances.
        """
        if self.collection.count() == 0:
            return []

        query_embedding = self.embedding_model.encode([query]).tolist()

        # Query more candidates to allow clearance filtering
        n_results = min(max(top_k * 4, 10), self.collection.count())

        res = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        matched: List[RetrievedChunk] = []
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        ids = res.get("ids", [[]])[0]
        distances = res.get("distances", [[]])[0]

        for chunk_id, text, meta, dist in zip(ids, docs, metas, distances):
            meta = meta or {}
            classification_str = meta.get("classification", "GENERAL")
            try:
                classification = DataClassification(classification_str)
            except Exception:
                classification = DataClassification.GENERAL

            # Enforce clearance filter
            if allowed_clearances is not None and classification not in allowed_clearances:
                continue

            # Convert cosine distance to similarity score
            score = max(0.0, round(1.0 - dist, 3))

            matched.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=text,
                    classification=classification,
                    similarity_score=score,
                    metadata=meta,
                )
            )

            if len(matched) >= top_k:
                break

        return matched

    def search_texts(self, query: str, top_k: int = 3) -> List[str]:
        """Compatibility method returning plain text results."""
        chunks = self.search(query=query, top_k=top_k)
        return [c.text for c in chunks]