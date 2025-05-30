import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from persona import prompt_engineering


def test_build_prompt():
    question = "테스트 질문입니다."
    prompt = prompt_engineering.build_prompt(question)
    assert "테스트 질문입니다." in prompt
    assert "김신건" in prompt
    print("프롬프트 생성 테스트 통과")


def test_persona_info():
    info = prompt_engineering.get_persona_info()
    assert info["name"] == "김신건"
    assert info["mbti"] == "ESTJ"
    print("페르소나 정보 테스트 통과")


if __name__ == "__main__":
    test_build_prompt()
    test_persona_info()
