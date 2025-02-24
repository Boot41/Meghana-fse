import jwt
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from ..models.user import UserPreferences

User = get_user_model()

def verify_oauth_token(provider: str, token: str) -> dict:
    """Verify OAuth token with the provider and return user information."""
    if provider == 'google':
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 200:
            return response.json()
    
    elif provider == 'github':
        response = requests.get(
            'https://api.github.com/user',
            headers={'Authorization': f'token {token}'}
        )
        if response.status_code == 200:
            user_data = response.json()
            # Get email since it's not included in user data
            email_response = requests.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f'token {token}'}
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_email = next(
                    (email['email'] for email in emails if email['primary']),
                    None
                )
                if primary_email:
                    user_data['email'] = primary_email
                    return user_data
    
    return None

def create_oauth_user(provider: str, oauth_data: dict) -> User:
    """Create or update user from OAuth data."""
    email = oauth_data.get('email')
    user = User.objects.filter(email=email).first()
    
    if not user:
        username = f"{provider}_{oauth_data.get('sub', oauth_data.get('id'))}"
        user = User.objects.create(
            username=username,
            email=email,
            first_name=oauth_data.get('given_name', ''),
            last_name=oauth_data.get('family_name', ''),
            profile_picture=oauth_data.get('picture', ''),
            is_verified=True,
            oauth_provider=provider,
            oauth_id=oauth_data.get('sub', oauth_data.get('id'))
        )
        UserPreferences.objects.create(user=user)
    
    return user

def generate_verification_token(user: User) -> str:
    """Generate email verification token."""
    return jwt.encode(
        {'user_id': str(user.id), 'type': 'email_verification'},
        settings.SECRET_KEY,
        algorithm='HS256'
    )

def send_verification_email(user: User):
    """Send email verification link to user."""
    token = generate_verification_token(user)
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    context = {
        'user': user,
        'verification_url': verification_url
    }
    
    html_message = render_to_string('emails/verify_email.html', context)
    
    send_mail(
        'Verify your email',
        '',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message
    )

def generate_password_reset_token(user: User) -> str:
    """Generate password reset token."""
    return jwt.encode(
        {'user_id': str(user.id), 'type': 'password_reset'},
        settings.SECRET_KEY,
        algorithm='HS256'
    )

def send_password_reset_email(user: User):
    """Send password reset link to user."""
    token = generate_password_reset_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    context = {
        'user': user,
        'reset_url': reset_url
    }
    
    html_message = render_to_string('emails/reset_password.html', context)
    
    send_mail(
        'Reset your password',
        '',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message
    )

def verify_password_reset_token(token: str) -> User:
    """Verify password reset token and return user."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'password_reset':
            return None
        return User.objects.get(id=payload['user_id'])
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return None
