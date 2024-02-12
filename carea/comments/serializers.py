from rest_framework import serializers
from .models import Comment
from users.serializers import UserSerializer
from users.models import User

class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        # 필요한 필드만을 지정
        fields = ['nickname']

class CommentSerializer(serializers.ModelSerializer):
    #user의 특정 정보 (닉네임 등)
    user_info = CustomUserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'post', 'content', 'user', 'user_info', 'created_at']