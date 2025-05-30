import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from db import chroma_tool, schema
from rag import retriever


def test_sqlite_search():
    # 테스트용 문서 추가
    title = "RAG테스트문서"
    content = "이것은 RAG 검색 테스트입니다."
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (title, content) VALUES (?, ?)", (title, content)
    )
    doc_id = cur.lastrowid
    conn.commit()
    conn.close()
    # 검색
    results = retriever.search_sqlite_documents("RAG")
    assert any(title in r[1] for r in results)
    # 정리
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    print("sqlite3 RAG 검색 테스트 통과")


def test_chroma_search():
    # 테스트용 문서 추가
    doc_id = 888
    content = "ChromaDB RAG 테스트 문서"
    chroma_tool.add_document_to_chroma(doc_id, content)
    results = retriever.search_chroma_documents("RAG")
    assert any("RAG" in doc for _, doc in results)
    # 정리
    client = chroma_tool.get_chroma()
    col = client.get_or_create_collection(chroma_tool.COLLECTION_NAME)
    col.delete(ids=[str(doc_id)])
    print("ChromaDB RAG 검색 테스트 통과")


if __name__ == "__main__":
    test_sqlite_search()
    test_chroma_search()
