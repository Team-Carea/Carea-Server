from django.urls import path

from . import views

urlpatterns = [
    # 랜덤 인증 문장 받고, 음성 파일 보낼 수 있는 화면
    path("stt", views.stt, name="stt"),
]