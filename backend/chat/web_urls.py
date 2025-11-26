from django.urls import path
from . import web_views

urlpatterns = [
    path('friends/', web_views.friends_list_view, name='chat-friends'),
    path('search/', web_views.search_users_view, name='chat-search'),
    path('invite/<int:user_id>/', web_views.send_invite_view, name='chat-invite'),
    path('request/<int:friendship_id>/<str:action>/', web_views.handle_request_view, name='chat-handle-request'),
]
