from agent.services.rag_service import RAGService
from document.models import Conversation
from rest_framework.response import Response
from rest_framework.views import APIView


class AskAPIView(APIView):
    def post(self, request):
        question = request.data.get("question")
        user_slack_id = request.data.get("user_slack_id")

        rag = RAGService()
        result = rag.ask(question)
        Conversation.objects.create(
            user=user_slack_id,
            user_message=question,
            assistant_message=result["answer"],
        )
        return Response(result)


class HealthAPIView(APIView):
    def get(self, request):
        return Response({"status": "ok"})
