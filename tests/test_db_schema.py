import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from db import schema


def test_db_init_and_tables():
    # DB 초기화
    schema.init_db()
    db_path = schema.DB_PATH
    assert db_path.exists(), f"DB 파일이 존재하지 않음: {db_path}"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # 각 테이블 존재 확인
    for table in ["documents", "conversations", "resumes"]:
        cur.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
        )
        assert cur.fetchone(), f"테이블 {table}이(가) 존재하지 않음"
    conn.close()
    print("DB 및 테이블 생성 테스트 통과")


if __name__ == "__main__":
    test_db_init_and_tables()
