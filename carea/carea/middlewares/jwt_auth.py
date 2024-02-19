from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from django.contrib.auth.models import AnonymousUser

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from users.models import User


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # url 쿼리 스트링에서 토큰 추출
        token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]

        try:
            # 토큰 유효성 검증 및 decode
            access_token = AccessToken(token)
            # 컨슈머의 scope를 유저 객체로 설정
            scope["user"] = await get_user(access_token["user_id"])
        except TokenError:
            scope["user"] = AnonymousUser()

        # 성공 시 유저 이메일, 실패 시 AnonymousUser 출력
        print("user: ", scope["user"])
        return await super().__call__(scope, receive, send)

def JwtAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))