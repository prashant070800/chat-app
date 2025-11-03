from django.contrib import admin
from django.urls import path, include

# --- Add these imports for Swagger ---
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# --- End of imports ---

# --- Add this Schema View for Swagger ---
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
    
    # Add this line to include all your app's API URLs
    # All URLs will be prefixed with 'api/'
    # e.g., /api/signup/, /api/login/, /api/logout/
    path('api/', include('core.urls')),

    # --- Add these paths for Swagger UI and ReDoc ---
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # --- End of Swagger paths ---
]

