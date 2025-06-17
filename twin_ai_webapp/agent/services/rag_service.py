import logging

from agent.utils.chroma_tool import search_chroma
from agent.utils.prompt_templates import get_prompt_template
from django.conf import settings
from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)


# LangChain 기반 RAG 서비스 (Ollama 기반)
class RAGService:
    def __init__(self, ollama_url=None, embed_model=None, instruct_model=None):
        self.ollama_url = ollama_url or settings.OLLAMA_BASE_URL
        self.embed_model = embed_model or settings.OLLAMA_EMBED_MODEL
        self.instruct_model = instruct_model or settings.OLLAMA_INSTRUCT_MODEL
        self.searching_model = settings.OLLAMA_SEARCHING_MODEL
        self.llm = Ollama(base_url=self.ollama_url, model=self.instruct_model)
        self.searching_llm = Ollama(
            base_url=self.ollama_url, model=self.searching_model
        )

    def search(self, query, top_k=3):
        return search_chroma(query, top_k=top_k)

    def iterative_search(self, user_question, max_iter=1, top_k=3):
        """
        사용자의 질문에 대해 LLM이 검색 쿼리를 생성하고, 반복적으로 vectorstore에서 자료를 찾음.
        """
        retrieved_docs = []
        used_queries = set()
        current_query = user_question
        for i in range(max_iter):
            system_prompt = (
                "당신은 사용자의 질문에 답하기 위해 필요한 자료(키워드/검색 쿼리)를 생성하는 검색 전문가입니다. "
                "질문에 답변하는 데 필요한 핵심 검색 쿼리를 생성하세요."
                "문서는 한글, 영어로 작성되어 있습니다."
            )
            user_prompt = f"질문: {current_query}"

            logger.info(f"Searching Query: {user_prompt}")
            search_query = self.searching_llm.invoke(
                f"<|system|>{system_prompt}<|end|>\n<|user|>{user_prompt}<|end|>\n검색 쿼리: ",
                temperature=0.2,
                max_tokens=64,
                stop=None,
            ).strip()
            logger.info(f"Searching Query: {search_query}")
            if not search_query or search_query in used_queries:
                break
            used_queries.add(search_query)

            docs = search_chroma(search_query, top_k=top_k)
            retrieved_docs.extend([d for d in docs if d not in retrieved_docs])
        return retrieved_docs

    def ask(self, user_question, chat_history=None):
        """
        iterative_search로 누적된 자료를 바탕으로 최종 답변을 생성
        
        Args:
            user_question (str): 사용자 질문
            chat_history (list): LangChain message 형식의 대화 기록 리스트
        """
        chat_history = chat_history or []
        retrieved_docs = self.search(user_question)
        
        # Create prompt template with retrieved documents
        chat_prompt = get_prompt_template(retrieved_docs)
        
        # Format the prompt with question and chat history
        messages = chat_prompt.format_messages(
            question=user_question,
            chat_history=chat_history
        )
        
        logger.info(f"Formatted Messages: {messages}")
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        return {
            "answer": response,
            "prompt": str(messages),
            "retrieved_docs": retrieved_docs,
        }
