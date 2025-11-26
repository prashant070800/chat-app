import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def login(email, password):
    response = requests.post(f"{BASE_URL}/login/", json={"email": email, "password": password})
    if response.status_code == 200:
        return response.cookies
    print(f"Login failed for {email}: {response.text}")
    return None

def signup(email, password, first_name, last_name):
    data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name
    }
    response = requests.post(f"{BASE_URL}/signup/", json=data)
    if response.status_code == 201:
        return response.cookies
    # If already exists, try login
    if "already exists" in response.text:
        return login(email, password)
    print(f"Signup failed for {email}: {response.text}")
    return None

def run_test():
    # 1. Signup/Login User A
    print("Logging in User A...")
    cookies_a = signup("usera@example.com", "password123", "User", "A")
    if not cookies_a: return

    # 2. Signup/Login User B
    print("Logging in User B...")
    cookies_b = signup("userb@example.com", "password123", "User", "B")
    if not cookies_b: return

    # 3. User A sends invite to User B
    print("User A sending invite to User B...")
    response = requests.post(
        f"{BASE_URL}/chat/friendship/send_invite/",
        json={"receiver_email": "userb@example.com"},
        cookies=cookies_a,
        headers={"X-CSRFToken": cookies_a.get('csrftoken', '')} # DRF might not need CSRF for API if using Token, but we are using Session/Cookie now? 
        # Wait, we are using TokenAuthentication in views? 
        # The viewset uses `permission_classes = [IsAuthenticated]`.
        # The default auth classes in settings.py are TokenAuthentication and SessionAuthentication.
        # If we send the cookie, SessionAuthentication should work.
        # But SessionAuthentication requires CSRF token for POST requests.
        # Let's see if we need to handle CSRF.
    )
    # Actually, if we use the `auth_token` cookie, we might need a custom authentication class that reads the token from the cookie,
    # OR we rely on the fact that we are NOT using SessionAuthentication for the API, but TokenAuthentication.
    # BUT, the browser sends the cookie.
    # If we want to use the cookie for API calls, we need to ensure the backend reads it.
    # Standard TokenAuthentication expects `Authorization: Token <token>` header.
    # It does NOT read from cookies by default.
    # I might have missed this in the implementation plan! 
    # The user asked for "token/jwt based http cookie".
    # This usually means we need a custom Authentication class that reads the token from the cookie.
    
    # Let's check if I implemented that. I did NOT.
    # I only set the cookie. I didn't tell DRF to read it.
    # So this test might fail with 401 Unauthorized if I don't send the header.
    # But the user wants cookie-based auth.
    
    # I will try to send the header first to verify the logic, then I will fix the auth to read from cookie.
    # Actually, let's see if I can fix it now.
    
    print(f"Send Invite Response: {response.status_code} {response.text}")

if __name__ == "__main__":
    run_test()
