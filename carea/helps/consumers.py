import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from google.cloud import speech

from users.models import User
from chats.models import ChatRoom

class HelpConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # URL 경로에서 채팅방 id 추출
            self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

            # 미들웨어로 JWT 유저 정보 추출
            self.user = self.scope["user"]

            # 채팅방 가져오기
            room = await self.get_room(self.room_id)

            # 채팅방에 참여하는 도움 요청자 및 제공자만 인증 가능
            if not await self.is_user_in_room(self.user, room):
                print('채팅방 참여자만 인증할 수 있습니다.')
                await self.close()

            # channel layer에 저장할 그룹 이름
            self.room_group_name = f"help_{self.room_id}"

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
    async def receive(self, text_data=None, bytes_data=None):
        try:
            # 그룹 이름 가져옴
            self.room_group_name = f"help_{self.room_id}"

            # 채팅방 가져오기
            room = await self.get_room(self.room_id)

            # 도움 제공자의 랜덤 생성한 문장인 경우
            # DB에 인증 문장 저장하고, 그룹에 문장 보내기
            if text_data:
                print(await self.check_helper(room))
                if not await self.check_helper(room):
                    print('도움 제공자만 인증할 문장을 보낼 수 있습니다.')
                    await self.send(text_data=json.dumps({'isSuccess': False, 'message': '도움 요청자만 인증할 문장을 말할 수 있습니다.'}))
                    await self.close()

                content = json.loads(text_data)

                # 수신된 JSON에서 필요한 정보 추출
                sentence = content['message']

                # 수신된 인증 문장 데이터베이스에 저장
                await self.save_sentence(room, sentence)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        "type": "help_message",
                        "message": sentence
                    }
                )

            # 도움 요청자의 바이너리 음성 파일인 경우
            # STT 써서 랜덤 문장 비교 후 DB에 포인트 업데이트, 결과 프론트로 보내기
            elif bytes_data:
                if not await self.check_helped(room):
                    print('도움 요청자만 인증할 문장을 말할 수 있습니다.')
                    await self.send(text_data=json.dumps({'isSuccess': False, 'message': '도움 요청자만 인증할 문장을 말할 수 있습니다.'}))
                    await self.close()

                transcription = await self.perform_stt(bytes_data)

                # 문장 비교
                if transcription == room.sentence:
                    # 성공 시 유저 경험치 상승
                    await self.increase_points(room)

                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name, {
                            "type": "help_message",
                            "message": transcription
                        }
                    )

                else:
                    # 실패 시 음성 파일 다시 보내라는 메시지 전송
                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name, {
                            "type": "help_message",
                            "message": transcription
                        }
                    )

        except ValueError as e:
            # 값 오류 처리
            await self.send(text_data=json.dumps({'isSuccess': False, 'message': str(e)}))

    # Receive message from room group
    async def help_message(self, event):
        try:
            message = event['message']

            # Send message to WebSocket (클라이언트로)
            await self.send(text_data=json.dumps({"message": message}))

        except Exception as e:
            # 일반 예외 처리
            await self.send(text_data=json.dumps({'isSuccess': False, 'message': str(e)}))

    async def perform_stt(self, bytes_data):
        client = speech.SpeechClient()

        audio = speech.RecognitionAudio(content=bytes_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="ko-KR",
            audio_channel_count=2,
        )

        # 음성 -> 텍스트
        response = client.recognize(config=config, audio=audio)
        transcription = response.results[0].alternatives[0].transcript

        return transcription

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
    def check_helper(self, room):
        return room.helper == self.user

    @database_sync_to_async
    def check_helped(self, room):
        return room.helped == self.user.id

    @database_sync_to_async
    def save_sentence(self, room, sentence):
        if not sentence:
            raise ValueError("인증 문장이 필요합니다.")

        # 채팅방 인증 문장 저장
        room.sentence = sentence
        room.save()

    @database_sync_to_async
    def increase_points(self, room):
        if not room:
            raise ValueError("채팅방 정보가 필요합니다.")

        # 유저 경험치 상승
        helped = User.objects.get(id=room.helped)
        helped.point += 5
        helped.save()

        helper = User.objects.get(id=room.helper.id)
        helper.point += 10
        helper.save()