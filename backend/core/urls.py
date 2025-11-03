from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserSignUpViewSet, CustomAuthTokenLoginView, UserLogoutView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'signup', UserSignUpViewSet, basename='signup')


# The API URLs are now determined automatically by the router.
# We also add custom paths for login and logout.
urlpatterns = [
    # Signup URL (e.g., POST /api/signup/)
    path('', include(router.urls)),
    
    # Login URL (e.g., POST /api/login/)
    path('login/', CustomAuthTokenLoginView.as_view(), name='api-login'),
    
    # Logout URL (e.g., POST /api/logout/)
    path('logout/', UserLogoutView.as_view(), name='api-logout'),
]