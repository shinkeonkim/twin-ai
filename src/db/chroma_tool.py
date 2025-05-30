import argparse
import hashlib

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

CHROMA_PATH = "chroma_data"
COLLECTION_NAME = "documents"


# 한글 지원 sentence-transformers 임베딩 (ko-sroberta-multitask)
def get_korean_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="jhgan/ko-sroberta-multitask"
    )


# ChromaDB 서버 인스턴스 생성 (docker-compose chroma-db)
def get_chroma():
    return chromadb.HttpClient(
        host="chroma-db", port=8000, settings=Settings(anonymized_telemetry=False)
    )


def add_document_to_chroma(doc_id: int, content: str):
    client = get_chroma()
    col = client.get_or_create_collection(
        COLLECTION_NAME, embedding_function=get_korean_embedding_function()
    )
    col.add(documents=[content], ids=[str(doc_id)])
    print(f"ChromaDB에 문서 {doc_id} 추가")


def delete_document_from_chroma(doc_id: int):
    client = get_chroma()
    col = client.get_or_create_collection(
        COLLECTION_NAME, embedding_function=get_korean_embedding_function()
    )
    col.delete(ids=[str(doc_id)])
    print(f"ChromaDB에서 문서 {doc_id} 삭제")


def list_chroma_documents():
    client = get_chroma()
    col = client.get_or_create_collection(
        COLLECTION_NAME, embedding_function=get_korean_embedding_function()
    )
    docs = col.get()
    for i, doc in enumerate(docs["documents"]):
        print(f"id={docs['ids'][i]}, content={doc}")


def simple_embed(text: str) -> list[float]:
    ef = get_korean_embedding_function()
    return ef([text])[0]


def main():
    parser = argparse.ArgumentParser(description="ChromaDB Tool")
    subparsers = parser.add_subparsers(dest="command")

    add_doc = subparsers.add_parser("add")
    add_doc.add_argument("--id", required=True, type=int)
    add_doc.add_argument("--content", required=True)
    list_doc = subparsers.add_parser("list")
    del_doc = subparsers.add_parser("delete")
    del_doc.add_argument("--id", required=True, type=int)

    args = parser.parse_args()
    if args.command == "add":
        add_document_to_chroma(args.id, args.content)
    elif args.command == "list":
        list_chroma_documents()
    elif args.command == "delete":
        delete_document_from_chroma(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
