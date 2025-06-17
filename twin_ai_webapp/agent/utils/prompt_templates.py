# Twin AI Prompt Templates
BASIC_PROMPT_TEMPLATE = """{{question}}

{document_template}
""".strip()

DOCUMENT_TEMPLATE = """
참고 내용:
아래 내용은 사용자의 질문과 관련된 참고 내용입니다. 사용자의 질문에 대한 답변을 작성할 때 참고하세요.
{docs}
"""


def get_prompt_template(retrieved_docs=[]):
    return BASIC_PROMPT_TEMPLATE.format(
        document_template=get_document_template(retrieved_docs),
    )


def get_document_template(retrieved_docs=[]):
    if retrieved_docs:
        return DOCUMENT_TEMPLATE.format(docs="\n".join(retrieved_docs))
    return ""
