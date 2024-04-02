from django.db.models import Q
from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from .serializers import ChatRoomSerializer, ChatSerializer
from .models import ChatRoom, Chat
from helps.models import Help

def index(request):
    return render(request, "index.html")


# 사용자 정의 예외 클래스 (예외 발생 시 즉각적인 HTTP 응답을 위해 사용)
class ImmediateResponseException(Exception):
    # 예외 인스턴스 생성 시 HTTP 응답 객체 받음
    def __init__(self, response):
        self.response = response

# 채팅방 목록 조회, 채팅방 생성
class ChatRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer

    # GET 요청에 대한 쿼리셋을 정의하는 메소드
    def get_queryset(self):
        # 요청으로부터 유저 가져옴
        user_id = self.request.user.id

        # 해당 id를 가진 사용자가 속한 채팅방들 찾기
        return ChatRoom.objects.filter(
            (Q(helped=user_id) | Q(helper=user_id)) & Q(updated_at__isnull=False)
        ).order_by('-updated_at')

    # GET 요청에 대한 커스텀 응답을 만드는 메소드 (list 메소드 오버라이드)
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = {
                'isSuccess': True,
                'message': '요청에 성공하였습니다.',
                'result': serializer.data
            }
            return Response(data)
        except Exception as e:
            content = {'isSuccess': False, 'message': str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 시리얼라이저의 context 설정
    def get_serializer_context(self):
        # 부모 클래스의 컨텍스트 가져오는 메소드 호출
        context = super(ChatRoomListCreateView, self).get_serializer_context()
        # 컨텍스트에 유저 추가
        context['user'] = self.request.user
        return context

    # POST 요청을 처리하여 새로운 리소스를 생성하는 메소드
    def create(self, request, *args, **kwargs):
        try:
            # 요청 body로부터 요청글 id 가져오기
            help_id = request.data.get('help')
            # 요청글 id 없는 경우
            if not help_id:
                return Response({'isSuccess': False, 'message': 'body에 도움 요청글 id가 필요합니다.'})

            serializer = self.perform_create(help_id)
        except ImmediateResponseException as e:
            # 즉각적인 응답이 필요할 경우 예외를 통해 응답 반환
            return e.response
        # 성공 헤더 생성
        headers = self.get_success_headers(serializer.data)
        return Response({'isSuccess': True, 'message': '요청에 성공하였습니다.',
                         'result': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    # 시리얼라이저를 통해 데이터베이스에 객체를 저장하는 메소드
    def perform_create(self, help_id):
        # 도움 요청글 객체
        help = Help.objects.get(id=help_id)

        # 요청글에서 도움 요청자 id 받아옴
        helped_id = help.user.id

        # 토큰을 통해 도움 제공자 객체 받아옴
        helper = self.request.user
        if helper.id == helped_id:
            # 본인의 요청글에서는 채팅방 생성 불가 (도움 제공자만 가능)
            raise ImmediateResponseException(Response(
                {'isSuccess': False, 'message': '본인의 도움 요청글에서는 채팅방을 만들 수 없습니다.'},
                status=status.HTTP_403_FORBIDDEN))

        # 요청글의 채팅방이 이미 있는지 확인
        existing_chatroom = ChatRoom.objects.filter(
            help=help,
            helped=helped_id,
            helper=helper
        ).first()

        # 이미 존재하는 채팅방이 있다면 해당 채팅방의 정보를 시리얼라이즈
        if existing_chatroom:
            serializer = ChatRoomSerializer(existing_chatroom, context=self.get_serializer_context())
            raise ImmediateResponseException(Response(
                {'isSuccess': True, 'message': '기존에 있던 채팅방 정보를 불러옵니다.',
                 'result': serializer.data}, status=status.HTTP_200_OK))

        # 없다면 새 채팅방 객체 생성 후 시리얼라이즈
        new_chatroom = ChatRoom.objects.create(help=help, helped=helped_id, helper=helper)
        return ChatRoomSerializer(new_chatroom, context=self.get_serializer_context())

# 채팅 메시지 목록 조회
class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer

    # GET 요청에 대한 쿼리셋을 정의하는 메소드
    def get_queryset(self):
        # URL 파라미터에서 'room_id' 값 가져옴
        room_id = self.kwargs.get('room_id')

        # room_id가 제공되지 않았을 경우, 404 Bad Request
        if not room_id:
            raise ValidationError('room_id 파라미터가 필요합니다.')

        room = ChatRoom.objects.get(id=room_id)
        user = self.request.user

        # 로그인한 유저가 채팅방 유저가 아닌 경우, 403 Forbidden
        if not (user.id == room.helped or user == room.helper):
            raise PermissionDenied('채팅방 참여자가 아닙니다.')

        return Chat.objects.filter(room=room)

    # GET 요청에 대한 커스텀 응답을 만드는 메소드 (list 메소드 오버라이드)
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = {
                'isSuccess': True,
                'message': '요청에 성공하였습니다.',
                'result': serializer.data
            }
            return Response(data)
        except PermissionDenied as e:
            content = {'isSuccess': False, 'message': str(e)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            content = {'isSuccess': False, 'message': str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)