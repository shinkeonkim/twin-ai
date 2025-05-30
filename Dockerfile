# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

WORKDIR /app

# Poetry 설치
RUN pip install --upgrade pip && pip install poetry

# 프로젝트 전체 복사
COPY . .

# Poetry install (모든 파일이 복사된 후)
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# API 서버 실행
CMD ["uvicorn", "src.server.api_server:app", "--host", "0.0.0.0", "--port", "8000"]

# Slack Bot 실행 예시 (빌드 후)
# docker run --env-file .env twin-ai python src/slackbot/bot.py
