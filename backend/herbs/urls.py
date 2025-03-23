from django.urls import path
from .views import HerbIdentificationView

urlpatterns = [
    path('identify/', HerbIdentificationView.as_view(), name='herb-identify'),
] 