from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.common.models import UUIDModel, TimeStampedModel
from apps.users.managers import CustomUserManager
import uuid

class User(AbstractBaseUser, PermissionsMixin, UUIDModel):
    """
    User model replicating src/models/user.model.js
    """
    ROLE_USER = 'user'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_ADMIN, 'Admin'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    is_email_verified = models.BooleanField(default=False)
    
    # Django specific fields for admin access
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class Token(TimeStampedModel):
    """
    Token model replicating src/models/token.model.js
    Used for Reset Password and Verify Email (stateful tokens).
    Refresh tokens are handled by SimpleJWT (stateless/blacklist).
    """
    TYPE_RESET_PASSWORD = 'resetPassword'
    TYPE_VERIFY_EMAIL = 'verifyEmail'
    # Refresh is handled by SimpleJWT, but we can store it here if we want strict equivalence.
    # For this port, we will stick to Django idioms where Refresh tokens are JWTs managed by the library,
    # and this model is used for the opaque/random tokens for emails.
    
    TOKEN_TYPE_CHOICES = [
        (TYPE_RESET_PASSWORD, 'Reset Password'),
        (TYPE_VERIFY_EMAIL, 'Verify Email'),
    ]

    token = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES)
    expires = models.DateTimeField()
    blacklisted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'

    def __str__(self):
        return f"{self.type} - {self.user.email}"