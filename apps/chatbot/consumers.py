from channels.generic.websocket import AsyncWebsocketConsumer

class ChatBotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('TEST MY CHAT BOT WEBSOCKET CONNECTION ...')
        await self.accept()