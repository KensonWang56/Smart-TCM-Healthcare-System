from django.urls import path
from .views import ChatView

urlpatterns = [
    path('message/', ChatView.as_view(), name='chat-message'),
] 