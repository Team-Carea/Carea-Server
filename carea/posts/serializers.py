from rest_framework import serializers
from .models import Post
from users.serializers import CustomUserDetailsSerializer
from users.models import User

class CustomUserSerializer(CustomUserDetailsSerializer):
    class Meta:
        model = User
        # 필요한 필드만을 지정
        fields = ['nickname']

class PostSerializer(serializers.ModelSerializer):
    # user의 특정 정보 (닉네임 등)
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'created_at', 'updated_at', 'user']