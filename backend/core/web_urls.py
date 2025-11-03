from django.urls import path
from django.contrib.auth import views as auth_views
from .web_views import home_view, signup_view # Import the new view
from .forms import EmailAuthenticationForm # Our custom form

urlpatterns = [
    # Home page (requires login)
    path('', home_view, name='web-home'),
    
    # Login view
    path('login/', auth_views.LoginView.as_view(
        template_name='core/registration/login.html',
        authentication_form=EmailAuthenticationForm # Use our custom form
    ), name='web-login'),
    
    # Logout view
    path('logout/', auth_views.LogoutView.as_view(
        template_name='core/registration/logged_out.html'
    ), name='web-logout'),

    # --- NEW SIGNUP URL ---
    path('signup/', signup_view, name='web-signup'),
]

