"""
Views for the accounts app (JWT auth).
"""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .serializers import LoginSerializer, UserSerializer


class LoginView(APIView):
    """
    POST /api/auth/login/
    Accepts username or email + password. Returns access and refresh tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LogoutView(TokenBlacklistView):
    """
    POST /api/auth/logout/
    Body: { "refresh": "<refresh_token>" }
    Blacklists the refresh token.
    """
    permission_classes = [AllowAny]


class RefreshView(TokenRefreshView):
    """
    POST /api/auth/refresh/
    Body: { "refresh": "<refresh_token>" }
    Returns new access token.
    """
    permission_classes = [AllowAny]


class MeView(APIView):
    """
    GET /api/auth/me/
    Returns the current authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
