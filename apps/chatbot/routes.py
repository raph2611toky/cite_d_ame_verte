from django.urls import path
from apps.chatbot.consumers import ChatBotConsumer

websocket_urlpatterns = [
    path('ws/chatbot/', ChatBotConsumer.as_asgi())
]