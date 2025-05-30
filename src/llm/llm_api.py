import os

import google.generativeai as genai
import openai
from dotenv import load_dotenv

load_dotenv()


def get_gemini_api_key():
    return os.environ.get("GEMINI_API_KEY", "dummy-gemini-key")


def get_openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "dummy-openai-key")


# Gemini API (google-generativeai SDK 사용)
def call_gemini_api(prompt: str) -> str:
    api_key = get_gemini_api_key()
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini API 오류] {e}"


# OpenAI(ChatGPT) API 호출
def call_openai_api(prompt: str) -> str:
    api_key = get_openai_api_key()
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=512,
            temperature=0.7,
            timeout=15,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI API 오류] {e}"


if __name__ == "__main__":
    p = "Twin AI의 목표는 무엇인가요?"
    print("Gemini:", call_gemini_api(p))
    print("OpenAI:", call_openai_api(p))
