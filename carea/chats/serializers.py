from rest_framework import serializers

from .models import Chat, ChatRoom
from users.models import User

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'message', 'created_at', 'user')

# 채팅방에 유저 정보를 붙이기 위한 시리얼라이저
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'nickname', 'profile_url')

class ChatRoomSerializer(serializers.ModelSerializer):
    # 동적으로 가져올 필드들
    latest_message = serializers.SerializerMethodField()
    opponent = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ('id', 'help', 'latest_message', 'updated_at', 'opponent')

    # 최신 메시지를 가져오는 메소드
    def get_latest_message(self, obj):
        latest_msg = Chat.objects.filter(room=obj).order_by('-created_at').first()
        if latest_msg:
            return latest_msg.message
        # 메시지가 없다면 None 반환
        return None

    # 상대방 정보를 가져오는 메소드
    def get_opponent(self, obj):
        request_user = self.context['user']
        # 요청한 사용자가 도움 요청자일 경우, 도움 제공자 반환
        if request_user.id == obj.helped:
            return UserSerializer(obj.helper).data
        # 그렇지 않다면, 도움 요청자 반환
        else:
            return UserSerializer(User.objects.get(id=obj.helped)).data