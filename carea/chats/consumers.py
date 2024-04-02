import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from users.models import User
from .models import ChatRoom, Chat

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # URL 경로에서 채팅방 id 추출
            self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

            # 미들웨어로 JWT 유저 정보 추출
            self.user = self.scope["user"]

            # 채팅방 가져오기
            room = await self.get_room(self.room_id)

            # 채팅방에 참여하는 도움 요청자 및 제공자만 채팅 가능
            if not await self.is_user_in_room(self.user, room):
                print('채팅방 참여자가 아닙니다.')
                await self.close()

            # channel layer에 저장할 그룹 이름
            self.room_group_name = f"chat_{self.room_id}"

            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

        except ValueError as e:
            # 값 오류가 있을 경우, 오류 메시지 보내고 연결 종료
            print(e)
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        except Exception as e:
            # 일반 예외 처리 (예: 오류 기록)
            pass

    # Receive message from WebSocket (클라이언트로부터)
    async def receive(self, text_data):
        content = json.loads(text_data)

        try:
            # 수신된 JSON에서 필요한 정보를 추출
            message = content['message']
            user_id = self.user.id

            # 그룹 이름 가져옴
            self.room_group_name = f"chat_{self.room_id}"

            # 채팅방 가져오기
            room = await self.get_room(self.room_id)

            # 수신된 메시지 데이터베이스에 저장
            await self.save_message(room, user_id, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "chat.message",
                    "message": message,
                    "user_id": user_id
                }
            )
        except ValueError as e:
            # 값 오류 처리
            await self.send(text_data=json.dumps({'isSuccess': False, 'message': str(e)}))

    # Receive message from room group
    async def chat_message(self, event):
        try:
            message = event['message']
            user_id = event['user_id']

            # Send message to WebSocket (클라이언트로)
            await self.send(text_data=json.dumps({"message": message, "user_id": user_id}))

        except Exception as e:
            # 일반 예외 처리
            await self.send(text_data=json.dumps({'isSuccess': False, 'message': str(e)}))

    @database_sync_to_async
    def get_room(self, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            return room
        except ChatRoom.DoesNotExist:
            raise ValueError("채팅방이 존재하지 않습니다.")

    @database_sync_to_async
    def is_user_in_room(self, user, room):
        return user == room.helper or user.id == room.helped

    @database_sync_to_async
    def save_message(self, room, user_id, message):
        if not user_id or not message:
            raise ValueError("사용자 id 및 메시지가 필요합니다.")

        # 메시지 생성하고 데이터베이스에 저장 (created_at은 auto_now_add=True로 현재 시간 자동 저장)
        Chat.objects.create(room=room, user=User.objects.get(id=user_id), message=message)
        # 채팅방 활성화된 시간 변경
        room.updated_at = timezone.now()
        room.save()