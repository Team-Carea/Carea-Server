import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from users.models import User
from .models import ChatRoom, Chat


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope["url_route"]["kwargs"]["room_id"]    # URL 경로에서 방 ID를 추출합니다.

            if not await self.check_room_exists(self.room_id):  # 방이 존재하는지 확인합니다.
                raise ValueError('채팅방이 존재하지 않습니다.')

            self.room_group_name = f"chat_{self.room_id}"

            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

        except ValueError as e:  # 값 오류가 있을 경우 (예: 방이 존재하지 않음), 오류 메시지를 보내고 연결을 종료합니다.
            await self.send({'error': str(e)})
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        except Exception as e:  # 일반 예외를 처리합니다 (예: 오류 기록).
            pass

    # Receive message from WebSocket
    async def receive(self, text_data):
        content = json.loads(text_data)

        try:
            # 수신된 JSON에서 필요한 정보를 추출합니다.
            message = content['message']
            sender_id = content['sender_id']
            helped_id = content.get('helped_id')
            helper_id = content.get('helper_id')
            help_id = content.get('help_id')

            # 두 id가 모두 제공되었는지 확인합니다.
            if not helped_id or not helper_id:
                raise ValueError("도움 요청자 및 제공자 id가 모두 필요합니다.")

            # 제공된 id를 사용하여 방을 가져오거나 생성합니다.
            room = await self.get_or_create_room(helped_id, helper_id, help_id)

            # room_id 속성을 업데이트합니다.
            self.room_id = str(room.id)

            # 그룹 이름을 가져옵니다.
            self.room_group_name = f"chat_{self.room_id}"

            # 수신된 메시지를 데이터베이스에 저장합니다.
            await self.save_message(room, sender_id, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "chat.message",
                    "message": message,
                    "sender_id": sender_id
                }
            )
        except ValueError as e:
            # 값 오류가 있을 경우, 오류 메시지를 전송합니다.
            await self.send(text_data=json.dumps({'error': str(e)}))

    # Receive message from room group
    async def chat_message(self, event):
        try:
            # 이벤트에서 메시지와 발신자 id를 추출합니다.
            message = event['message']
            sender_id = event['sender_id']  # 발신자 id 정보 추출

            # Send message to WebSocket
            await self.send(text_data=json.dumps({"message": message, "sender_id": sender_id}))

        except Exception as e:
            # 일반 예외를 처리하여 오류 메시지를 보냅니다.
            await self.send(text_data=json.dumps({'error': '메시지 전송 실패'}))

    @database_sync_to_async
    def check_room_exists(self, room_id):
        # 주어진 ID로 채팅방이 존재하는지 확인합니다.
        return ChatRoom.objects.filter(id=room_id).exists()

    @database_sync_to_async
    def get_or_create_room(self, helped_id, helper_id, help_id):
        try:
            # 제공된 id를 사용하여 방을 가져옵니다.
            room = ChatRoom.objects.get(helped=helped_id, helper=helper_id, help=help_id)
            return room
        except ChatRoom.DoesNotExist:
            # 방이 존재하지 않으면 값 오류를 발생시킵니다.
            raise ValueError("채팅방이 존재하지 않습니다.")

    @database_sync_to_async
    def save_message(self, room, sender_id, message_text):
        # 발신자 이메일과 메시지 텍스트가 제공되었는지 확인합니다.
        if not sender_id or not message_text:
            raise ValueError("발신자 id 및 메시지 텍스트가 필요합니다.")

        # 메시지를 생성하고 데이터베이스에 저장합니다.
        # timestamp 필드는 auto_now_add=True 속성 때문에 자동으로 현재 시간이 저장됩니다.
        Chat.objects.create(room=room, user=User.objects.get(id=sender_id), message=message_text)