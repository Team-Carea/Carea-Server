from rest_framework import serializers

from .models import Chat, ChatRoom

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class ChatRoomSerializer(serializers.ModelSerializer):
    latest_message = serializers.SerializerMethodField()  # 최신 메시지 필드를 동적으로 가져옵니다.
    # opponent_id = serializers.SerializerMethodField()  # 상대방 id 필드를 동적으로 가져옵니다.
    # opponent_nickname
    # opponent_profile_url
    # 오히려 나중엔 helped, helper 안 넣을 수도
    class Meta:
        model = ChatRoom  # ChatRoom 모델을 기반으로 합니다.
        # 시리얼라이즈할 필드들을 지정합니다.
        fields = ('id', 'help', 'helped', 'helper', 'latest_message')

    # 최신 메시지를 가져오는 메소드입니다.
    def get_latest_message(self, obj):
        latest_msg = Chat.objects.filter(room=obj).order_by('-created_at').first()  # 최신 메시지를 조회합니다.
        if latest_msg:
            return latest_msg.message  # 최신 메시지의 내용을 반환합니다.
        return None  # 메시지가 없다면 None을 반환합니다.

    # 요청 사용자와 대화하는 상대방의 id를 가져오는 메소드입니다.
    # def get_opponent_id(self, obj):
    #    request_user_id = self.kwargs.get('user_id')
    #   # 요청한 사용자가 도움 요청자일 경우, 도움 제공자의 id를 반환합니다.
    #     if request_user_id == obj.helped:
    #         return obj.helper
    #     else:  # 그렇지 않다면, 도움 요청자의 id를 반환합니다.
    #         return obj.helped



