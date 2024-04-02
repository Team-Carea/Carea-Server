from django.urls import path

from . import views

urlpatterns = [
    # 채팅 화면
    path("", views.index, name="index"),

    # 채팅방 목록 조회: GET /chats/rooms/
    # 채팅방 생성: POST /chats/rooms/
    path("rooms/", views.ChatRoomListCreateView.as_view(), name="chat_rooms"),

    # 채팅 메시지 목록 조회: GET /chats/{room_id}/messages/
    path("<int:room_id>/messages/", views.ChatListView.as_view(), name="chat_messages"),
]