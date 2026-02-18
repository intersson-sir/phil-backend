"""
Serializers for the accounts app.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login. Accepts either 'username' or 'email' (or both) + password.
    """
    username = serializers.CharField(required=False, allow_blank=True, write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        # Frontend may send "username" and/or "email" — use either as login identifier
        login_value = (attrs.get('username') or attrs.get('email') or '').strip()
        password = attrs.get('password')

        if not login_value or not password:
            raise serializers.ValidationError(
                {'detail': 'Provide username or email and password.'}
            )

        user = User.objects.filter(
            Q(username__iexact=login_value) | Q(email__iexact=login_value)
        ).first()

        if user is None:
            raise serializers.ValidationError({'detail': 'Invalid credentials.'})

        if not user.check_password(password):
            raise serializers.ValidationError({'detail': 'Invalid credentials.'})

        if not user.is_active:
            raise serializers.ValidationError({'detail': 'User account is disabled.'})

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for current user (GET /api/auth/me/)."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
        read_only_fields = fields
