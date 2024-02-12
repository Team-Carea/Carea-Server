from allauth.account.adapter import get_adapter

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer


class CustomRegisterSerializer(RegisterSerializer):
    # 기본 설정 필드: email, password
    # 추가 설정 필드: nickname, profile_url, introduction
    nickname = serializers.CharField(max_length=10)
    profile_url = serializers.CharField(max_length=255)
    introduction = serializers.CharField(max_length=100)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname', '')
        data['profile_url'] = self.validated_data.get('profile_url', '')
        data['introduction'] = self.validated_data.get('introduction', '')

        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.nickname = self.cleaned_data.get('nickname')
        user.profile_url = self.cleaned_data.get('profile_url')
        user.introduction = self.cleaned_data.get('introduction')
        user.save()
        adapter.save_user(request, user, self)
        return user