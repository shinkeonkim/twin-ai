from .prompt_templates import get_prompt_template


def build_prompt(question: str, retrieved_docs=None) -> str:
    template = get_prompt_template(retrieved_docs)
    return template.replace("{question}", question)
