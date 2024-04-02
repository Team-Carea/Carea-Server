from django.urls import re_path

from . import consumers

websocket_helps_urlpatterns = [
    re_path(r"ws/helps/stt/(?P<room_id>\w+)$", consumers.HelpConsumer.as_asgi()),
]