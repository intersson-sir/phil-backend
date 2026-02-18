"""
Middleware for JWT token verification on API requests.
Sets request.user from Bearer token when present and valid.
"""
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    For requests to /api/, attempts to authenticate using JWT from
    Authorization: Bearer <token> header and sets request.user.
    """
    def process_request(self, request):
        if not request.path.startswith('/api/'):
            return
        auth = JWTAuthentication()
        try:
            result = auth.authenticate(request)
            if result is not None:
                request.user, request.auth = result
        except (InvalidToken, AuthenticationFailed):
            pass
