from django.urls import path
from apps.users import views

urlpatterns = [
    # ==========================================
    # Auth Routes
    # ==========================================
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/logout', views.LogoutView.as_view(), name='logout'),
    path('auth/refresh-tokens', views.RefreshTokensView.as_view(), name='refresh-tokens'),
    path('auth/forgot-password', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password', views.ResetPasswordView.as_view(), name='reset-password'),
    path('auth/send-verification-email', views.SendVerificationEmailView.as_view(), name='send-verification-email'),
    path('auth/verify-email', views.VerifyEmailView.as_view(), name='verify-email'),

    # ==========================================
    # User Routes
    # ==========================================
    path('users', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<str:userId>', views.UserDetailView.as_view(), name='user-detail'),
]