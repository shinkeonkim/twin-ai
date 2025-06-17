from agent.services.rag_service import RAGService
from document.models import Conversation
from rest_framework.response import Response
from rest_framework.views import APIView
from langchain.schema import HumanMessage, AIMessage


class AskAPIView(APIView):
    def post(self, request):
        question = request.data.get("question")
        user_slack_id = request.data.get("user_slack_id")
        chat_history = request.data.get("chat_history", [])

        # Convert chat history to LangChain message format
        messages = []
        for msg in chat_history:
            if msg["role"] == "human":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        rag = RAGService()
        result = rag.ask(question, messages)
        
        # Store the conversation
        Conversation.objects.create(
            user=user_slack_id,
            user_message=question,
            assistant_message=result["answer"],
        )
        return Response(result)


class HealthAPIView(APIView):
    def get(self, request):
        return Response({"status": "ok"})
