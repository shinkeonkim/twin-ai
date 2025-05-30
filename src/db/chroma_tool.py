import argparse
import hashlib

import chromadb
from chromadb.config import Settings

CHROMA_PATH = "chroma_data"
COLLECTION_NAME = "documents"


# 임시 임베딩: 텍스트를 해시로 변환해 벡터화 (실제 LLM 임베딩은 이후 구현)
def simple_embed(text: str):
    h = hashlib.sha256(text.encode()).digest()
    return [b for b in h[:8]]


# ChromaDB 인스턴스 생성
def get_chroma():
    return chromadb.Client(Settings(persist_directory=CHROMA_PATH))


def add_document_to_chroma(doc_id: int, content: str):
    client = get_chroma()
    col = client.get_or_create_collection(COLLECTION_NAME)
    embedding = simple_embed(content)
    col.add(documents=[content], ids=[str(doc_id)], embeddings=[embedding])
    print(f"ChromaDB에 문서 {doc_id} 추가")


def list_chroma_documents():
    client = get_chroma()
    col = client.get_or_create_collection(COLLECTION_NAME)
    docs = col.get()
    for i, doc in enumerate(docs["documents"]):
        print(f"id={docs['ids'][i]}, content={doc}")


def main():
    parser = argparse.ArgumentParser(description="ChromaDB Tool")
    subparsers = parser.add_subparsers(dest="command")

    add_doc = subparsers.add_parser("add")
    add_doc.add_argument("--id", required=True, type=int)
    add_doc.add_argument("--content", required=True)
    list_doc = subparsers.add_parser("list")

    args = parser.parse_args()
    if args.command == "add":
        add_document_to_chroma(args.id, args.content)
    elif args.command == "list":
        list_chroma_documents()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
