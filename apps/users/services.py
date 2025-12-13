import logging
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from apps.users.models import User, Token
from apps.common.exceptions import api_exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError
from datetime import timedelta
import secrets

logger = logging.getLogger(__name__)

# ==============================================================================
# TOKEN SERVICE
# ==============================================================================

def generate_auth_tokens(user):
    """
    Generate Access and Refresh JWTs.
    Matches src/services/token.service.js -> generateAuthTokens
    """
    refresh = JWTRefreshToken.for_user(user)
    
    return {
        'access': {
            'token': str(refresh.access_token),
            'expires': timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        },
        'refresh': {
            'token': str(refresh),
            'expires': timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        }
    }

def generate_opaque_token(user, token_type, expiration_minutes):
    """
    Generates a random string token (not JWT) for Reset Password / Verify Email.
    """
    token_str = secrets.token_urlsafe(32)
    expires = timezone.now() + timedelta(minutes=expiration_minutes)
    
    # Save to DB
    Token.objects.create(
        token=token_str,
        user=user,
        type=token_type,
        expires=expires
    )
    return token_str

def verify_token(token_str, token_type):
    """
    Verify opaque token.
    Matches src/services/token.service.js -> verifyToken
    """
    try:
        token_doc = Token.objects.get(token=token_str, type=token_type, blacklisted=False)
        if token_doc.expires < timezone.now():
            raise ValidationError('Token expired')
        return token_doc
    except Token.DoesNotExist:
        raise NotFound('Token not found')

# ==============================================================================
# EMAIL SERVICE
# ==============================================================================

def send_email(to, subject, text):
    """
    Wrapper for Django send_mail
    """
    try:
        send_mail(
            subject=subject,
            message=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            fail_silently=False,
        )
        logger.info(f"Email sent to {to}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def send_reset_password_email(to_email, token):
    """
    Matches src/services/email.service.js -> sendResetPasswordEmail
    """
    subject = 'Reset password'
    # In real app, use settings.BACKEND_URL or frontend URL
    reset_url = f"http://localhost:3000/reset-password?token={token}"
    text = f"Dear user,\nTo reset your password, click on this link: {reset_url}\nIf you did not request any password resets, then ignore this email."
    send_email(to_email, subject, text)

def send_verification_email(to_email, token):
    """
    Matches src/services/email.service.js -> sendVerificationEmail
    """
    subject = 'Email Verification'
    verify_url = f"http://localhost:3000/verify-email?token={token}"
    text = f"Dear user,\nTo verify your email, click on this link: {verify_url}\nIf you did not create an account, then ignore this email."
    send_email(to_email, subject, text)

# ==============================================================================
# AUTH SERVICE
# ==============================================================================

def login_user_with_email_and_password(email, password):
    """
    Matches src/services/auth.service.js -> loginUserWithEmailAndPassword
    """
    try:
        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect email or password')
        return user
    except User.DoesNotExist:
        raise AuthenticationFailed('Incorrect email or password')

def logout_user(refresh_token_str):
    """
    Matches src/services/auth.service.js -> logout
    Blacklists the JWT refresh token.
    """
    try:
        token = JWTRefreshToken(refresh_token_str)
        token.blacklist()
    except TokenError:
        raise NotFound('Not found') # Matching Regular behavior which throws 404 if token not found

def refresh_auth(refresh_token_str):
    """
    Matches src/services/auth.service.js -> refreshAuth
    """
    try:
        refresh = JWTRefreshToken(refresh_token_str)
        
        # In SimpleJWT, we can't easily get the user object from just the object without decoding
        # But we can create a new access token.
        # To match Regular EXACTLY (return both tokens), we regenerate both.
        user_id = refresh['user_id']
        user = User.objects.get(id=user_id)
        
        # Blacklist old one
        refresh.blacklist()
        
        # Generate new pair
        return generate_auth_tokens(user)
    except (TokenError, User.DoesNotExist):
        raise AuthenticationFailed('Please authenticate')

def reset_password(token_str, new_password):
    """
    Matches src/services/auth.service.js -> resetPassword
    """
    try:
        token_doc = verify_token(token_str, Token.TYPE_RESET_PASSWORD)
        user = token_doc.user
        
        user.set_password(new_password)
        user.save()
        
        # Delete all reset tokens for this user (Consume token)
        Token.objects.filter(user=user, type=Token.TYPE_RESET_PASSWORD).delete()
    except Exception:
         raise AuthenticationFailed('Password reset failed')

def verify_email(token_str):
    """
    Matches src/services/auth.service.js -> verifyEmail
    """
    try:
        token_doc = verify_token(token_str, Token.TYPE_VERIFY_EMAIL)
        user = token_doc.user
        
        user.is_email_verified = True
        user.save()
        
        Token.objects.filter(user=user, type=Token.TYPE_VERIFY_EMAIL).delete()
    except Exception:
        raise AuthenticationFailed('Email verification failed')