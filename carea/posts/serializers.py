from rest_framework import serializers
from .models import Post
from users.models import User

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 필요한 필드만을 지정
        fields = ['nickname', 'profile_url']

class PostSerializer(serializers.ModelSerializer):

    #user의 특정 정보 (닉네임 등)
    user= CustomUserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'created_at', 'updated_at', 'user']

class UserNicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 카테고리별 목록 조회시에는 닉네임만 출력하도록 함
        fields = ['nickname']

class CategoryPostSerializer(serializers.ModelSerializer):
    user= UserNicknameSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'created_at', 'updated_at', 'user']
