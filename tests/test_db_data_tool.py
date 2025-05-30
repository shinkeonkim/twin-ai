import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from db import data_tool, schema


def test_add_and_list_document():
    title = "테스트 문서2"
    content = "테스트 내용2"
    data_tool.add_document(title, content)
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, content FROM documents WHERE title=?", (title,))
    row = cur.fetchone()
    assert row and row[0] == title and row[1] == content
    cur.execute("DELETE FROM documents WHERE title=?", (title,))
    conn.commit()
    conn.close()
    print("문서 입력/조회 테스트 통과")


def test_add_and_list_conversation():
    user = "테스트유저"
    message = "테스트 메시지"
    data_tool.add_conversation(user, message)
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user, message FROM conversations WHERE user=?", (user,))
    row = cur.fetchone()
    assert row and row[0] == user and row[1] == message
    cur.execute("DELETE FROM conversations WHERE user=?", (user,))
    conn.commit()
    conn.close()
    print("대화 입력/조회 테스트 통과")


def test_add_and_list_resume():
    section = "테스트섹션"
    content = "테스트 이력"
    data_tool.add_resume(section, content)
    conn = schema.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT section, content FROM resumes WHERE section=?", (section,))
    row = cur.fetchone()
    assert row and row[0] == section and row[1] == content
    cur.execute("DELETE FROM resumes WHERE section=?", (section,))
    conn.commit()
    conn.close()
    print("이력서 입력/조회 테스트 통과")


if __name__ == "__main__":
    test_add_and_list_document()
    test_add_and_list_conversation()
    test_add_and_list_resume()
