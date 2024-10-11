from django.urls import path
from .views import CatastropheListView

urlpatterns = [
    path('api/catastrophes/', CatastropheListView.as_view(), name='catastrophe-list'),
]
