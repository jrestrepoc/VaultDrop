from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.core.domain import ConflictError
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from apps.users.serializers import (
    RegisterInputSerializer,
    LoginInputSerializer,
    UserOutputSerializer,
    AuthResponseSerializer,
)
from apps.users.services import UserService


class RegisterAPIView(APIView):
    """Expositor DRF para el caso de uso registrar usuario.
    
    No contiene lógica de negocio: delega estrictamente en UserService.
    Maneja códigos HTTP empresariales:
      - 201 Created: registro exitoso con token generado.
      - 400 Bad Request: formato inválido o datos de negocio inválidos.
      - 409 Conflict: username o email ya registrados en el sistema.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserService().register(**serializer.validated_data)
        except ConflictError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_409_CONFLICT)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            'token': token.key,
            'user': UserOutputSerializer(user).data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """Expositor DRF para autenticación y obtención de Token."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)

        if not user:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            'token': token.key,
            'user': UserOutputSerializer(user).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        from apps.users.serializers import ProfileInputSerializer
        from apps.core.account import account_snapshot
        serializer = ProfileInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService().update_profile(request.user, **serializer.validated_data)
        return Response({'account': account_snapshot(user)})
