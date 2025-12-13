from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.users.models import User

# ==============================================================================
# BASE SERIALIZERS
# ==============================================================================

class UserSerializer(serializers.ModelSerializer):
    """
    Output serializer for User object.
    Hides private fields like password.
    """
    id = serializers.UUIDField(format='hex') # Ensures ID looks like "5ebac..."

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'is_email_verified']


# ==============================================================================
# AUTH SERIALIZERS (VALIDATION)
# ==============================================================================

class RegisterSerializer(serializers.ModelSerializer):
    """
    Validates registration payload.
    Matches auth.validation.js -> register
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Validates login payload.
    Matches auth.validation.js -> login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    """
    Matches auth.validation.js -> logout
    """
    refresh_token = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    """
    Matches auth.validation.js -> refreshTokens
    """
    refresh_token = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Matches auth.validation.js -> forgotPassword
    """
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """
    Matches auth.validation.js -> resetPassword
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    token = serializers.CharField() # Passed in Query Param in Regular, here we can accept in body or query


class VerifyEmailSerializer(serializers.Serializer):
    """
    Matches auth.validation.js -> verifyEmail
    """
    token = serializers.CharField()


# ==============================================================================
# USER MANAGEMENT SERIALIZERS
# ==============================================================================

class CreateUserSerializer(serializers.ModelSerializer):
    """
    Admin creating a user.
    Matches user.validation.js -> createUser
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Updating user details.
    Matches user.validation.js -> updateUser
    """
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, write_only=True, validators=[validate_password])
    name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'name']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance