"""
ASGI config for carea project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from carea.middlewares.jwt_auth import JwtAuthMiddlewareStack
from chats.routing import websocket_chats_urlpatterns
from helps.routing import websocket_helps_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carea.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JwtAuthMiddlewareStack(
                URLRouter(
                    websocket_chats_urlpatterns + websocket_helps_urlpatterns
                )
            ),
        ),
    }
)