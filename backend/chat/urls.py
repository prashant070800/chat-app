from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FriendshipViewSet
from .api_views import MessageViewSet

router = DefaultRouter()
router.register(r'friendship', FriendshipViewSet, basename='friendship')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
