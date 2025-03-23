from django.urls import path
from .views import LoginView, LogoutView, CaptchaView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('captcha/', CaptchaView.as_view(), name='captcha'),
] 