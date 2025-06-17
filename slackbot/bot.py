import os

import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "dummy-bot-token")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "dummy-app-token")
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://api:8080/api/ask/")
MAX_THREAD_HISTORY = 5  # Maximum number of messages to fetch from thread history

app = App(token=SLACK_BOT_TOKEN)


def get_thread_history(client, channel_id, thread_ts, bot_user_id):
    """Get conversation history from a thread, excluding bot's own messages."""
    try:
        # Fetch thread replies
        result = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts,
            limit=MAX_THREAD_HISTORY
        )
        
        if not result["ok"]:
            return []

        # Filter out bot's own messages and format the conversation history
        messages = []
        for msg in reversed(result["messages"]):  # Reverse to get oldest first
            # Skip bot's own messages
            if msg.get("user") == bot_user_id:
                continue
                
            # Get the actual message content, removing any mentions
            text = msg["text"]
            # Remove bot mention from the message
            text = text.replace(f"<@{bot_user_id}>", "").strip()
            
            messages.append({
                "role": "human",
                "content": text
            })

        return messages
    except Exception as e:
        print(f"Error fetching thread history: {e}", flush=True)
        return []


@app.event("app_mention")
def handle_mention(event, say, client):
    print("[Slack Event] app_mention:", event, flush=True)
    user = event["user"]
    text = event["text"]
    channel_id = event["channel"]
    thread_ts = event.get("thread_ts") or event["ts"]
    bot_user_id = client.auth_test()["user_id"]

    # Remove bot mention from the question
    question = text.replace(f"<@{bot_user_id}>", "").strip()
    
    # Get thread history
    chat_history = get_thread_history(client, channel_id, thread_ts, bot_user_id)
    
    # API 서버에 질문 전달
    try:
        resp = requests.post(
            API_SERVER_URL, 
            json={
                "question": question, 
                "user_slack_id": user,
                "chat_history": chat_history
            }, 
            timeout=120
        )
        if resp.status_code == 200:
            answer = resp.json().get("answer", "(응답 없음)")
        else:
            answer = f"API 서버 오류: {resp.status_code} {resp.text}"
    except Exception as e:
        answer = f"API 서버 연결 실패: {e}"
    
    say(f"<@{user}> {answer}", thread_ts=thread_ts)


if __name__ == "__main__":
    print("Slack Bot 실행...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
