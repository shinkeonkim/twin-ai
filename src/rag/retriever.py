import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import chroma_tool, schema


# sqlite3에서 질문과 유사한 문서 검색 (간단히 LIKE)
def search_sqlite_documents(query: str, top_k=3):
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, content FROM documents WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
        (f"%{query}%", top_k),
    )
    results = cur.fetchall()
    conn.close()
    return results


# ChromaDB에서 임베딩 유사도 기반 검색 (simple_embed 사용)
def search_chroma_documents(query: str, top_k=3):
    client = chroma_tool.get_chroma()
    col = client.get_or_create_collection(
        chroma_tool.COLLECTION_NAME,
        embedding_function=chroma_tool.get_korean_embedding_function(),
    )
    results = col.query(query_texts=[query], n_results=top_k)
    docs = (
        list(zip(results["ids"][0], results["documents"][0])) if results["ids"] else []
    )
    return docs


if __name__ == "__main__":
    # 테스트: sqlite3 검색
    print("sqlite3 검색:", search_sqlite_documents("테스트"))
    # 테스트: ChromaDB 검색
    print("ChromaDB 검색:", search_chroma_documents("테스트"))
