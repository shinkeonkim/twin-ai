import logging
import os
import re

from django.db import transaction
from document.models.document import Document
from document.models.obsidian_file import ObsidianFile
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

OBSIDIAN_DIRECTORY = (
    "/Users/koa/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecondBrain"
)


def remove_code_blocks(text, block_types=("compressed-json",)):
    for block_type in block_types:
        pattern = re.compile(rf"```{block_type}[\s\S]*?```", re.MULTILINE)
        text = pattern.sub("", text)
    return text


def remove_frontmatter(text):
    # 문서 맨 앞에 --- ... --- 블럭이 있으면 제거
    return re.sub(r"^---[\s\S]*?---\s*", "", text, flags=re.MULTILINE)


def sync_obsidian_directory(
    directory_path=OBSIDIAN_DIRECTORY, chunk_size=1000, overlap=100
):
    """
    지정된 디렉토리 내의 모든 마크다운 파일을 Document로 동기화
    """
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if not file.endswith(".md"):
                continue
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            # 1. 코드블럭/메타데이터 제거
            text = remove_code_blocks(text, block_types=("compressed-json",))
            text = remove_frontmatter(text)
            # 2. ObsidianFile get_or_create
            obsidian_file, _ = ObsidianFile.objects.get_or_create(
                file_path=file_path, defaults={"file_name": file}
            )
            # 3. 기존 연결 Document 삭제
            Document.objects.filter(obsidian_file=obsidian_file).delete()
            # 4. 텍스트 분할 (더 자연스러운 분할)
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=overlap, separators=["\n\n", "\n"]
            )
            chunks = splitter.split_text(text)
            # 5. Document 여러 개 생성
            for idx, chunk in enumerate(chunks):
                Document.objects.create(
                    title=f"{file} (part {idx+1})",
                    content=chunk,
                    obsidian_file=obsidian_file,
                )
            logger.info(
                f"Obsidian 파일 동기화 완료: {file_path} ({len(chunks)}개 Document)"
            )
