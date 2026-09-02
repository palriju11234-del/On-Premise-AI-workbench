from pathlib import Path
from .vectorstore import LocalVectorStore


def ingest_knowledge():

    store = LocalVectorStore()

    documents = []

    knowledge_dir = Path("data/knowledge")

    for file in knowledge_dir.glob("*.txt"):

        text = file.read_text(
            encoding="utf-8"
        )

        documents.append({
            "filename": file.name,
            "text": text
        })

    store.add_documents(documents)

    return len(documents)