from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    FaceLoginView,
    UserInfoView,
    PasswordChangeView,
    AvatarUploadView,
    FaceUploadView
)

urlpatterns = [
    # 认证相关
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('face-login/', FaceLoginView.as_view(), name='face-login'),
    
    # 用户信息相关
    path('info/', UserInfoView.as_view(), name='user-info'),
    path('password/', PasswordChangeView.as_view(), name='change-password'),
    path('avatar/', AvatarUploadView.as_view(), name='upload-avatar'),
    path('face/', FaceUploadView.as_view(), name='manage-face'),
] 