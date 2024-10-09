from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.evenements.views import EvenementListView, EvenementProfileView, EvenementNewView, EvenementProfileFindView, EvenementFilterView

urlpatterns = [
    path('evenements/list/', EvenementListView.as_view(), name='evenement-list'), # GET
    path('evenements/new/', EvenementNewView.as_view(), name='evenement-new'), # POST
    path('evenement/<int:pk>/', EvenementProfileView.as_view(), name='evenement-detail'),# PUT, DELETE
    path('evenement/find/<int:pk>/', EvenementProfileFindView.as_view(), name='find_evenement'), # GET
    path('evenements/filter/', EvenementFilterView.as_view(), name='evenemt filter'), # GET
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)