from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.evenements.views import EvenementListView, EvenementProfileView, EvenementNewView

urlpatterns = [
    path('evenements/', EvenementListView.as_view(), name='evenement-list'),
    path('evenements/new/', EvenementNewView.as_view(), name='evenement-new'),
    path('evenements/<int:pk>/', EvenementProfileView.as_view(), name='evenement-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)