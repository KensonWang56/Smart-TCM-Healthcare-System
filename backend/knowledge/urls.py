from django.urls import path
from .views import KnowledgeView

urlpatterns = [
    path('', KnowledgeView.as_view(), name='knowledge-list'),
    path('<str:category>/', KnowledgeView.as_view(), name='knowledge-detail'),
] 