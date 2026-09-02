import chromadb
from sentence_transformers import SentenceTransformer


class LocalVectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="data/vector_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="enterprise_knowledge"
        )

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def add_documents(self, documents):

        texts = [d["text"] for d in documents]

        embeddings = self.embedding_model.encode(
            texts
        ).tolist()

        ids = [
            f"doc_{i}"
            for i in range(len(texts))
        ]

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings
        )

    def search(self, query, top_k=3):

        embedding = self.embedding_model.encode(
            [query]
        ).tolist()

        result = self.collection.query(
            query_embeddings=embedding,
            n_results=top_k
        )

        return result["documents"][0]