import logging

from agent.utils.chroma_tool import search_chroma
from agent.utils.prompt_engineering import build_prompt
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

    # def ask(self, question, top_k=3):
    #     retrieved_docs = self.search(question, top_k=top_k)
    #     print(retrieved_docs)
    #     prompt = build_prompt(question, retrieved_docs)
    #     logger.info(f"Prompt: {prompt}")
    #     answer = self.llm.invoke(
    #         prompt,
    #         temperature=0.3,
    #         max_tokens=1000,
    #         top_p=0.9,
    #         frequency_penalty=0.0,
    #         presence_penalty=0.0,
    #         stop=None,
    #         stream=False,
    #         logprobs=None,
    #     )
    #     return {
    #         'answer': answer,
    #         'prompt': prompt,
    #         'retrieved_docs': retrieved_docs,
    # }

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

    def ask(self, user_question):
        """
        iterative_search로 누적된 자료를 바탕으로 최종 답변을 생성
        """
        retrieved_docs = self.search(user_question)

        prompt = build_prompt(user_question, retrieved_docs)

        logger.info(f"Iterative Prompt: {prompt}")
        answer = self.llm.invoke(
            prompt,
            temperature=0.4,
            top_p=0.9,
            stop=None,
        )
        return {
            "answer": answer,
            "prompt": prompt,
            "retrieved_docs": retrieved_docs,
        }
