import os

import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "dummy-bot-token")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "dummy-app-token")
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://localhost:8080/ask")

app = App(token=SLACK_BOT_TOKEN)


@app.event("app_mention")
def handle_mention(event, say):
    print("[Slack Event] app_mention:", event, flush=True)
    user = event["user"]
    text = event["text"]
    thread_ts = event.get("thread_ts") or event["ts"]
    # API 서버에 질문 전달
    try:
        resp = requests.post(
            API_SERVER_URL, json={"question": text, "model": "gemini"}, timeout=10
        )
        if resp.status_code == 200:
            answer = resp.json().get("answer", "(응답 없음)")
        else:
            answer = f"API 서버 오류: {resp.status_code}"
    except Exception as e:
        answer = f"API 서버 연결 실패: {e}"
    say(f"<@{user}> {answer}", thread_ts=thread_ts)


if __name__ == "__main__":
    print("Slack Bot 실행...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
