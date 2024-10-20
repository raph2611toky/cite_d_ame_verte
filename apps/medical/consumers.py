import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.channel_layer:
            raise ValueError("Le backend de layer n'est pas configuré correctement.")
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_chat_{self.room_name}'
           
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f'CONNECTED to {self.room_group_name} ......')
        #print(self.scope)    

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print('DISCONNECTED from group ......')

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            if 'offer' in text_data_json:
                print('SEND OFFER ..\n')
            elif 'answer' in text_data_json:
                print('SEND ANSWER ..\n')
            elif 'candidate' in text_data_json:
                print('SEND CANDIDATE ...')
            offer = text_data_json.get('offer')
            answer = text_data_json.get('answer')
            candidate = text_data_json.get('candidate')
            message = text_data_json.get('message')
            
            if message is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'video_chat_message',
                        'message': message
                    }
                )
            if offer:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'video_chat_signal',
                        'offer': offer
                    }
                )
            if answer:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'video_chat_signal',
                        'answer': answer
                    }
                )
            if candidate:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'video_chat_signal',
                        'candidate': candidate
                    }
                )
        except json.JSONDecodeError:
            print("Erreur dans la réception du message.")
        await self.send(text_data=json.dumps({'error': 'Invalid message format'}))

    async def video_chat_message(self, event):
        message = event['message']
        
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def video_chat_signal(self, event):
        await self.send(text_data=json.dumps({
            'offer': event.get('offer'),
            'answer': event.get('answer'),
            'candidate': event.get('candidate')
        }))
