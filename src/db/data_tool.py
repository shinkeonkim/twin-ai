import argparse

from .schema import get_connection, init_db


def add_document(title, content):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (title, content) VALUES (?, ?)", (title, content)
    )
    conn.commit()
    conn.close()
    print("문서 추가 완료")


def list_documents():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, created_at FROM documents")
    for row in cur.fetchall():
        print(row)
    conn.close()


def add_conversation(user, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversations (user, message) VALUES (?, ?)", (user, message)
    )
    conn.commit()
    conn.close()
    print("대화 추가 완료")


def list_conversations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, user, message, created_at FROM conversations")
    for row in cur.fetchall():
        print(row)
    conn.close()


def add_resume(section, content):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resumes (section, content) VALUES (?, ?)", (section, content)
    )
    conn.commit()
    conn.close()
    print("이력서 항목 추가 완료")


def list_resumes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, section, created_at FROM resumes")
    for row in cur.fetchall():
        print(row)
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Twin AI DB Data Tool")
    subparsers = parser.add_subparsers(dest="command")

    # 문서
    doc_add = subparsers.add_parser("add_doc")
    doc_add.add_argument("--title", required=True)
    doc_add.add_argument("--content", required=True)
    doc_list = subparsers.add_parser("list_doc")

    # 대화
    conv_add = subparsers.add_parser("add_conv")
    conv_add.add_argument("--user", required=True)
    conv_add.add_argument("--message", required=True)
    conv_list = subparsers.add_parser("list_conv")

    # 이력서
    res_add = subparsers.add_parser("add_resume")
    res_add.add_argument("--section", required=True)
    res_add.add_argument("--content", required=True)
    res_list = subparsers.add_parser("list_resume")

    args = parser.parse_args()
    if args.command == "add_doc":
        add_document(args.title, args.content)
    elif args.command == "list_doc":
        list_documents()
    elif args.command == "add_conv":
        add_conversation(args.user, args.message)
    elif args.command == "list_conv":
        list_conversations()
    elif args.command == "add_resume":
        add_resume(args.section, args.content)
    elif args.command == "list_resume":
        list_resumes()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
