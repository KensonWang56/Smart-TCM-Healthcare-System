from django.urls import path
from .views import TongueAnalysisView

urlpatterns = [
    path('analyze/', TongueAnalysisView.as_view(), name='tongue-analyze'),
] 