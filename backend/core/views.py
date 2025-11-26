from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import UserSerializer, CustomAuthTokenSerializer

class UserSignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    A ViewSet for user registration (sign up).
    
    Provides a 'create' action:
    POST /api/signup/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] # Anyone can sign up

    def create(self, request, *args, **kwargs):
        """
        Handle user creation. On success, also generate and return an auth token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            {
                'user': serializer.data,
                'token': token.key
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class CustomAuthTokenLoginView(ObtainAuthToken):
    """
    A view for user login.
    
    Provides an action:
    POST /api/login/
    
    Returns a token on successful login.
    """
    permission_classes = [AllowAny] # Anyone can try to log in

    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class UserLogoutView(APIView):
    """
    A view for user logout.
    
    Provides an action:
    POST /api/logout/
    
    Deletes the user's auth token, invalidating their session.
    """
    permission_classes = [IsAuthenticated] # Only authenticated users can log out

    def post(self, request, *args, **kwargs):
        try:
            # Delete the token to log the user out
            request.user.auth_token.delete()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "Error logging out: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )
