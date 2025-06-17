import argparse
import hashlib
import os

import chromadb
import requests
from chromadb.config import Settings
from django.conf import settings

COLLECTION_NAME = settings.CHROMA_COLLECTION_NAME
CHROMA_DB_HOST = settings.CHROMA_DB_HOST
CHROMA_DB_PORT = settings.CHROMA_DB_PORT


# Ollama embedding API 호출
def ollama_embed(text: str) -> list[float]:
    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": settings.OLLAMA_EMBED_MODEL, "prompt": text}
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["embedding"]


# ChromaDB 서버 인스턴스 생성 (docker-compose chroma-db)
def get_chroma():
    return chromadb.HttpClient(
        host=CHROMA_DB_HOST,
        port=CHROMA_DB_PORT,
        settings=Settings(anonymized_telemetry=False),
    )


def add_document_to_chroma(doc_id: str, content: str):
    client = get_chroma()
    col = client.get_or_create_collection(COLLECTION_NAME)
    embedding = ollama_embed(content)
    col.upsert(documents=[content], ids=[doc_id], embeddings=[embedding])
    print(f"ChromaDB에 문서 {doc_id} 추가")


def update_document_in_chroma(doc_id: str, content: str):
    client = get_chroma()
    col = client.get_or_create_collection(COLLECTION_NAME)
    embedding = ollama_embed(content)
    col.upsert(documents=[content], ids=[doc_id], embeddings=[embedding])
    print(f"ChromaDB에 문서 {doc_id} 업데이트")


def delete_document_from_chroma(doc_id: str):
    client = get_chroma()
    col = client.get_or_create_collection(COLLECTION_NAME)
    col.delete(ids=[doc_id])
    print(f"ChromaDB에서 문서 {doc_id} 삭제")


def list_chroma_documents():
    client = get_chroma()
    col = client.get_or_create_collection(COLLECTION_NAME)
    docs = col.get()
    for i, doc in enumerate(docs["documents"]):
        print(f"id={docs['ids'][i]}, content={doc}")


def search_chroma(query: str, top_k: int = 3):
    client = get_chroma()
    col = client.get_or_create_collection(COLLECTION_NAME)
    embedding = ollama_embed(query)
    docs = col.query(query_embeddings=[embedding], n_results=top_k)
    return docs["documents"][0] if docs["documents"] else []
