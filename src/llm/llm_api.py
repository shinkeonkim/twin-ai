import os

import google.generativeai as genai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_gemini_api_key():
    return os.environ.get("GEMINI_API_KEY", "dummy-gemini-key")


def get_openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "dummy-openai-key")


# Gemini API (google-generativeai SDK 사용)
def call_gemini_api(prompt: str) -> str:
    print("GEMINI API 호출")
    print(prompt)
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
    print("OPENAI API 호출")
    print(prompt)
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(model="gpt-4.1", input=prompt)
        return response.output_text.strip()
    except Exception as e:
        return f"[OpenAI API 오류] {e}"


if __name__ == "__main__":
    p = "Twin AI의 목표는 무엇인가요?"
    print("Gemini:", call_gemini_api(p))
    print("OpenAI:", call_openai_api(p))
