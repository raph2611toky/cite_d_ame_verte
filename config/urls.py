from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.client.urls')),
    path('api/', include('apps.evenements.urls')),
    path('api/', include('apps.formations.urls')),
    path('api/', include('apps.marketplace.urls')),
]
