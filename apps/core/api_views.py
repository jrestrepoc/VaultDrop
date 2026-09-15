from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.core.account import account_snapshot

class AccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(account_snapshot(request.user))
