from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
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
        except ValueError as exc:
            msg = str(exc)
            # Reglas de negocio de duplicados corresponden a 409 Conflict
            if 'ya está en uso' in msg or 'ya está registrado' in msg or 'ya están registrados' in msg:
                return Response({'error': msg}, status=status.HTTP_409_CONFLICT)
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

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

