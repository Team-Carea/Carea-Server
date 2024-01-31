from django.urls import path

from . import views

urlpatterns = [
    # 채팅 시작 화면
    path("", views.index, name="index"),

    # 채팅방 목록 조회: GET /chats/{user_id}/rooms
    path("<int:user_id>/rooms", views.ChatRoomListCreateView.as_view(), name="chat_rooms"),

    # 채팅 시작: POST /chats/start
    path("start", views.chat_start, name="start"),

    # 채팅 메시지 목록 조회: GET /chats/{room_id}/messages
    path("<int:room_id>/messages", views.ChatListView.as_view(), name="chat_messages"),

    # 채팅: WS /chats/{room_id} 다른 튜토리얼
    # path("<int:room_id>", views.room, name="room"),
]