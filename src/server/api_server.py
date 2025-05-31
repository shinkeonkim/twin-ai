import os
import sys
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db import chroma_tool, schema
from llm import llm_api
from persona import prompt_engineering
from rag import retriever

app = FastAPI(docs_url="/swagger")


class AskRequest(BaseModel):
    question: str
    model: str = "gemini"  # 'gemini' or 'openai'


# --- 문서 관리 웹 UI 및 API ---
@app.get("/docs", response_class=HTMLResponse)
def list_docs():
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, sync_status, sync_at, created_at FROM documents ORDER BY id DESC"
    )
    docs = cur.fetchall()
    conn.close()
    html = """
    <h1>문서 목록</h1>
    <a href='/docs/new'>[문서 추가]</a>
    <table border=1 cellpadding=5>
    <tr><th>ID</th><th>제목</th><th>싱크상태</th><th>싱크일자</th><th>생성일</th><th>액션</th></tr>
    """
    for doc in docs:
        html += f"<tr><td>{doc[0]}</td><td><a href='/docs/{doc[0]}'>{doc[1]}</a></td><td>{doc[2]}</td><td>{doc[3] or ''}</td><td>{doc[4]}</td>"
        html += f"<td><a href='/docs/{doc[0]}/sync'>[ChromaSync]</a> <a href='/docs/{doc[0]}/edit'>[수정]</a> <a href='/docs/{doc[0]}/delete' onclick=\"return confirm('삭제?')\">[삭제]</a></td></tr>"
    html += "</table>"
    return html


@app.get("/docs/new", response_class=HTMLResponse)
def new_doc_form():
    return """
    <h2>문서 추가</h2>
    <form method='post' action='/docs/new'>
    제목: <input name='title'><br>
    내용:<br><textarea name='content' rows=10 cols=60></textarea><br>
    <button type='submit'>추가</button>
    </form>
    <a href='/docs'>[목록]</a>
    """


@app.post("/docs/new")
def add_doc(title: str = Form(...), content: str = Form(...)):
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (title, content, sync_status) VALUES (?, ?, 'not_synced')",
        (title, content),
    )
    doc_id = cur.lastrowid
    conn.commit()
    conn.close()
    return RedirectResponse(f"/docs/{doc_id}/sync", status_code=303)


@app.get("/docs/{doc_id}", response_class=HTMLResponse)
def doc_detail(doc_id: int):
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, content, sync_status, sync_at, created_at FROM documents WHERE id=?",
        (doc_id,),
    )
    doc = cur.fetchone()
    conn.close()
    if not doc:
        return "<h2>문서 없음</h2><a href='/docs'>[목록]</a>"
    html = f"""
    <h2>문서 상세</h2>
    <b>ID:</b> {doc[0]}<br>
    <b>제목:</b> {doc[1]}<br>
    <b>내용:</b><br><pre>{doc[2]}</pre><br>
    <b>싱크상태:</b> {doc[3]}<br>
    <b>싱크일자:</b> {doc[4] or ''}<br>
    <b>생성일:</b> {doc[5]}<br>
    <a href='/docs/{doc[0]}/sync'>[ChromaSync]</a> <a href='/docs/{doc[0]}/edit'>[수정]</a> <a href='/docs/{doc[0]}/delete' onclick=\"return confirm('삭제?')\">[삭제]</a> <a href='/docs'>[목록]</a>
    """
    return html


@app.get("/docs/{doc_id}/edit", response_class=HTMLResponse)
def edit_doc_form(doc_id: int):
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, content FROM documents WHERE id=?", (doc_id,))
    doc = cur.fetchone()
    conn.close()
    if not doc:
        return "<h2>문서 없음</h2><a href='/docs'>[목록]</a>"
    return f"""
    <h2>문서 수정</h2>
    <form method='post' action='/docs/{doc_id}/edit'>
    제목: <input name='title' value='{doc[0]}'><br>
    내용:<br><textarea name='content' rows=10 cols=60>{doc[1]}</textarea><br>
    <button type='submit'>수정</button>
    </form>
    <a href='/docs/{doc_id}'>[상세]</a>
    """


@app.post("/docs/{doc_id}/edit")
def edit_doc(doc_id: int, title: str = Form(...), content: str = Form(...)):
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE documents SET title=?, content=?, sync_status='not_synced', sync_at=NULL WHERE id=?",
        (title, content, doc_id),
    )
    conn.commit()
    conn.close()
    return RedirectResponse(f"/docs/{doc_id}/sync", status_code=303)


@app.get("/docs/{doc_id}/delete")
def delete_doc(doc_id: int):
    # chroma에서도 삭제
    try:
        chroma_tool.delete_document_from_chroma(doc_id)
    except Exception as e:
        print(f"Chroma에서 문서 삭제 실패: {e}")
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/docs", status_code=303)


@app.get("/docs/{doc_id}/sync")
def sync_doc(doc_id: int):
    # sqlite3에서 문서 조회
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM documents WHERE id=?", (doc_id,))
    doc = cur.fetchone()
    if not doc:
        conn.close()
        return RedirectResponse("/docs", status_code=303)
    # chroma에 추가/업데이트
    chroma_tool.add_document_to_chroma(doc[0], doc[1])
    # 싱크 상태/일자 갱신
    cur.execute(
        "UPDATE documents SET sync_status='synced', sync_at=? WHERE id=?",
        (datetime.now(), doc_id),
    )
    conn.commit()
    conn.close()
    return RedirectResponse(f"/docs/{doc_id}", status_code=303)


# --- 기존 LLM/RAG API ---
@app.post("/ask")
def ask(req: AskRequest):
    # ChromaDB 기반 RAG 검색
    rag_results = retriever.search_chroma_documents(req.question, top_k=3)
    # 문서 내용만 추출
    retrieved_docs = [doc for _, doc in rag_results]
    prompt = prompt_engineering.build_prompt(req.question, retrieved_docs)
    if req.model == "gemini":
        answer = llm_api.call_gemini_api(prompt)
    else:
        answer = llm_api.call_openai_api(prompt)
    return {"answer": answer, "prompt": prompt, "retrieved_docs": retrieved_docs}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("server.api_server:app", host="0.0.0.0", port=8000, reload=True)
