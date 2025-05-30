from .prompt_templates import PERSONA, get_prompt_template


def build_prompt(question: str, retrieved_docs=None) -> str:
    template = get_prompt_template()
    docs_text = ""
    if retrieved_docs:
        docs_text = "\n\n---\n참고 문서:\n" + "\n".join(retrieved_docs)
    return template.replace("{question}", question + docs_text)


def get_persona_info():
    return PERSONA


if __name__ == "__main__":
    # 테스트: 프롬프트 생성
    q = "오늘의 날씨는 어떤가요?"
    docs = ["문서1 내용", "문서2 내용"]
    print(build_prompt(q, docs))
