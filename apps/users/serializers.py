from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=8, write_only=True, required=True)


class LoginInputSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'steam_username')
        read_only_fields = fields


class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserOutputSerializer()


class ProfileInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    steam_username = serializers.CharField(max_length=100, allow_blank=True, default='')
