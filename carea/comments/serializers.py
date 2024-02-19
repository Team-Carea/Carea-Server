from rest_framework import serializers
from .models import Comment
from users.models import User

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 필요한 필드만을 지정
        fields = ['nickname', 'profile_url']

class CommentSerializer(serializers.ModelSerializer):
    #user의 특정 정보 (닉네임 등)
    user = CustomUserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'content', 'created_at','user']
