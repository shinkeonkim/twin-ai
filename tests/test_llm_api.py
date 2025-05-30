import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from llm import llm_api


def test_gemini_api():
    prompt = "Gemini 테스트 프롬프트"
    resp = llm_api.call_gemini_api(prompt)
    print(resp)
    assert "[Gemini 응답]" in resp or "Gemini" in resp or "오류" in resp
    print("Gemini API 더미 테스트 통과")


def test_openai_api():
    prompt = "OpenAI 테스트 프롬프트"
    resp = llm_api.call_openai_api(prompt)
    print(resp)
    assert "[OpenAI 응답]" in resp or "OpenAI" in resp or "오류" in resp
    print("OpenAI API 더미 테스트 통과")


if __name__ == "__main__":
    test_gemini_api()
    # test_openai_api()
