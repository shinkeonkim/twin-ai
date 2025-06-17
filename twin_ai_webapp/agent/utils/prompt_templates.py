# Twin AI Prompt Templates

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

def escape_braces(text):
    return text.replace('{', '{{').replace('}', '}}')

def get_prompt_template(retrieved_docs=[]):
    document_message = ""

    if retrieved_docs:
        # 슬랙 메시지 등 외부 입력에 포함된 중괄호 이스케이프 처리
        safe_docs = [escape_braces(doc) for doc in retrieved_docs]
        retrieved_docs_str = "\n".join(safe_docs)
        document_message = f"""
        아래 내용은 사용자 질문을 김신건에 대한 정보를 저장한 문서에서 검색한 참고 내용입니다. 
        메세지를 작성할 때 참고하세요.
        {retrieved_docs_str}
        """

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", document_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])
    
    return chat_prompt
