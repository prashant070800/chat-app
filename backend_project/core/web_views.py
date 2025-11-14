from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm # Import the new form

@login_required
def home_view(request):
    """
    This is the main home page view.
    It requires the user to be logged in.
    If not logged in, Django will redirect to the LOGIN_URL.
    """
    # You can pass context to the template
    context = {
        'user': request.user
    }
    return render(request, 'core/registration/home.html', context)
# --- NEW SIGNUP VIEW ---
def signup_view(request):
    """
    Handle user registration.
    """
    if request.user.is_authenticated:
        return redirect('web-home') # Already logged in, redirect to home

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in directly
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('web-home') # Redirect to home page
    else:
        form = UserRegistrationForm()
        
    return render(request, 'core/registration/signup.html', {'form': form})

