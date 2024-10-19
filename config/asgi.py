import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.chatbot.routes import websocket_urlpatterns
import apps.medical.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    "websocket": URLRouter(websocket_urlpatterns + apps.medical.routing.websocket_urlpatterns)
})