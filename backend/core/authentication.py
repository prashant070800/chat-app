from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        # Check if 'auth_token' is in cookies
        token = request.COOKIES.get('auth_token')
        if not token:
            return super().authenticate(request)
        
        return self.authenticate_credentials(token)
