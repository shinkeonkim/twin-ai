import logging
import os
import re

import pdfplumber
from django.db import transaction
from document.models import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def clean_pdf_text(text):
    # 연속된 줄바꿈/공백 정리
    text = re.sub(r"\n{3,}", "\n\n", text)  # 3줄 이상 → 2줄
    text = re.sub(r"[ \t]+", " ", text)  # 연속 공백 → 1칸
    return text.strip()


def extract_tables(page):
    tables = page.extract_tables()
    md_tables = []

    def safe_row(row):
        return [str(cell) if cell is not None else "" for cell in row]

    for table in tables:
        if not table:
            continue
        # 마크다운 테이블로 변환
        header = "| " + " | ".join(safe_row(table[0])) + " |"
        sep = "| " + " | ".join(["---"] * len(table[0])) + " |"
        rows = ["| " + " | ".join(safe_row(row)) + " |" for row in table[1:]]
        md_tables.append("\n".join([header, sep] + rows))
    return "\n\n".join(md_tables)


def process_pdf_and_create_documents(pdf_file_instance):
    logger = logging.getLogger(__name__)
    pdf_path = pdf_file_instance.file.path
    logger.info(f"[PDF 처리 시작] 파일: {pdf_path}")

    all_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                text = clean_pdf_text(text)
                # 표 추출 및 마크다운 테이블로 삽입
                md_tables = extract_tables(page)
                if md_tables:
                    text += f"\n\n[표]\n{md_tables}"
                logger.info(f"[페이지 {i+1}] 텍스트 길이: {len(text)}")
                all_text.append(text)
    except Exception as e:
        logger.error(f"PDF 파싱 실패: {e}")
        return

    full_text = "\n".join(all_text)
    logger.info(f"[전체 텍스트 길이] {len(full_text)}")

    # 더 자연스러운 분할
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", "•", "·", "▶", "▪", "●"],
    )
    chunks = splitter.split_text(full_text)
    logger.info(f"[분할된 청크 개수] {len(chunks)}")

    with transaction.atomic():
        for idx, chunk in enumerate(chunks):
            title = f"{os.path.basename(pdf_path)} - part {idx+1}"
            doc = Document(
                title=title,
                content=chunk,
                pdf_file=pdf_file_instance,
            )
            doc.save()
            logger.info(
                f"[Document 저장] uuid: {doc.uuid}, title: {title}, 길이: {len(chunk)}"
            )
    logger.info("[PDF 처리 및 Document 저장 완료]")
