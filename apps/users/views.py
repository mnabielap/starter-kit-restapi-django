from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.users import serializers, services
from apps.users.models import User, Token
from apps.users.permissions import IsAdmin, IsUserOrAdmin
from apps.common.utils import pick

# ==============================================================================
# AUTH CONTROLLERS
# ==============================================================================

class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        tokens = services.generate_auth_tokens(user)
        user_data = serializers.UserSerializer(user).data
        
        return Response({'user': user_data, 'tokens': tokens}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    @extend_schema(request=serializers.LoginSerializer, responses=serializers.UserSerializer)
    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = services.login_user_with_email_and_password(email, password)
        tokens = services.generate_auth_tokens(user)
        user_data = serializers.UserSerializer(user).data
        
        return Response({'user': user_data, 'tokens': tokens})

class LogoutView(APIView):
    @extend_schema(request=serializers.LogoutSerializer)
    def post(self, request):
        serializer = serializers.LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.logout_user(serializer.validated_data['refresh_token'])
        return Response(status=status.HTTP_204_NO_CONTENT)

class RefreshTokensView(APIView):
    @extend_schema(request=serializers.RefreshTokenSerializer)
    def post(self, request):
        serializer = serializers.RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = services.refresh_auth(serializer.validated_data['refresh_token'])
        return Response(tokens)

class ForgotPasswordView(APIView):
    @extend_schema(request=serializers.ForgotPasswordSerializer)
    def post(self, request):
        serializer = serializers.ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        # Regular boilerplate throws 404 if user not found inside generateResetPasswordToken
        try:
            user = User.objects.get(email=email)
            token = services.generate_opaque_token(user, Token.TYPE_RESET_PASSWORD, services.settings.JWT_RESET_PASSWORD_EXPIRATION_MINUTES)
            services.send_reset_password_email(email, token)
        except User.DoesNotExist:
            # Security: Don't reveal if user exists or not, but Regular throws 404, so we follow Regular
             return Response({'code': 404, 'message': 'No users found with this email'}, status=status.HTTP_404_NOT_FOUND)
             
        return Response(status=status.HTTP_204_NO_CONTENT)

class ResetPasswordView(APIView):
    @extend_schema(request=serializers.ResetPasswordSerializer, parameters=[OpenApiParameter('token', str)])
    def post(self, request):
        # Token is passed as Query Param in Regular
        token = request.query_params.get('token')
        if not token:
             return Response({'code': 400, 'message': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.ResetPasswordSerializer(data={'password': request.data.get('password'), 'token': token})
        serializer.is_valid(raise_exception=True)
        
        services.reset_password(token, serializer.validated_data['password'])
        return Response(status=status.HTTP_204_NO_CONTENT)

class SendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = services.generate_opaque_token(request.user, Token.TYPE_VERIFY_EMAIL, services.settings.JWT_VERIFY_EMAIL_EXPIRATION_MINUTES)
        services.send_verification_email(request.user.email, token)
        return Response(status=status.HTTP_204_NO_CONTENT)

class VerifyEmailView(APIView):
    @extend_schema(parameters=[OpenApiParameter('token', str)])
    def post(self, request):
        token = request.query_params.get('token')
        if not token:
             return Response({'code': 400, 'message': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        services.verify_email(token)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# USER CONTROLLERS
# ==============================================================================

class UserListCreateView(generics.ListCreateAPIView):
    """
    Handles GET /users and POST /users
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateUserSerializer
        return serializers.UserSerializer

    def get_permissions(self):
        # POST /users -> Admin only (manageUsers)
        # GET /users -> Admin only (getUsers)
        return [IsAuthenticated(), IsAdmin()]

    def filter_queryset(self, queryset):
        # Implement filtering: name, role
        name = self.request.query_params.get('name')
        role = self.request.query_params.get('role')
        sort_by = self.request.query_params.get('sortBy') # field:desc
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if role:
            queryset = queryset.filter(role=role)
            
        if sort_by:
            # Convert 'name:desc' to '-name'
            parts = sort_by.split(':')
            field = parts[0]
            order = parts[1] if len(parts) > 1 else 'asc'

            field_mapping = {
                'createdAt': 'created_at',
                'updatedAt': 'updated_at',
                'isEmailVerified': 'is_email_verified'
            }
            field = field_mapping.get(field, field)

            if order == 'desc':
                field = '-' + field
            queryset = queryset.order_by(field)
            
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles GET, PATCH, DELETE /users/:userId
    """
    queryset = User.objects.all()
    lookup_url_kwarg = 'userId'
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return serializers.UpdateUserSerializer
        return serializers.UserSerializer

    def get_permissions(self):
        # GET -> User can see self, Admin can see all
        # PATCH -> User can update self, Admin can update all
        # DELETE -> Admin only (manageUsers)
        
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdmin()]
        
        return [IsAuthenticated(), IsUserOrAdmin()]