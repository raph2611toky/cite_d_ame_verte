import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.medical.models import VideoCallSession

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print('CONNECTED .....')

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print('DISCONNECTED ....')

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        offer = text_data_json.get('offer')
        answer = text_data_json.get('answer')
        candidate = text_data_json.get('candidate')
        if message is not None or message!='':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_chat_message',
                    'message': message
                }
            )
        elif offer and answer and candidate:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_chat_signal',
                    'offer': offer,
                    'answer': answer,
                    'candidate': candidate,
                }
            )
        else:
            print('Informations incomplet .........')

    async def video_chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def video_chat_signal(self, event):
        # Envoyer le signal WebRTC à tous les participants
        await self.send(text_data=json.dumps({
            'offer': event.get('offer'),
            'answer': event.get('answer'),
            'candidate': event.get('candidate'),
        }))