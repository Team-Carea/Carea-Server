from django.urls import re_path

from . import consumers

websocket_chats_urlpatterns = [
    re_path(r"ws/chats/(?P<room_id>\w+)$", consumers.ChatConsumer.as_asgi()),
]