from django.contrib import admin
from django.urls import path, include

# --- Imports for Swagger ---
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# --- Schema View for Swagger ---
schema_view = get_schema_view(
   openapi.Info(
      title="Your Project API",
      default_version='v1',
      description="API documentation for your user authentication system",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourproject.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
# --- End of Schema View ---

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- YOUR API URLS ---
    # This points to core/urls.py (the file you listed)
    # Access via /api/signup/, /api/login/
    path('api/', include('core.urls')), 

    # --- YOUR NEW WEB APP URLS ---
    # This points to core/web_urls.py
    # Access via /login/, /logout/, /signup/, /
    path('', include('core.web_urls')),

    # --- Additional API URLs ---
    path("api/chat/", include("chat.urls")),
    path("api/", include("notifications.urls")),
    path("chat/", include("chat.web_urls")),

    # --- Swagger URLs ---
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
