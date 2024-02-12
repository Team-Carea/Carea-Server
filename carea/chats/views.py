from django.db.models import Q
from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from .serializers import ChatRoomSerializer, ChatSerializer
from .models import ChatRoom, Chat
from helps.models import Help
from users.models import User

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
        try:
            # 요청의 path variable에서 'user_id' 값 가져옴
            user_id = self.kwargs.get('user_id')

            if not user_id:
                raise ValidationError('user_id 파라미터가 필요합니다.')

            # 해당 id를 가진 사용자가 속한 채팅방들 찾기
            return ChatRoom.objects.filter(
                Q(helped=user_id) | Q(helper=user_id)
            ).order_by('-updated_at')
        except ValidationError as e:
            content = {'isSuccess': False, 'message': e.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 다른 종류의 예외 발생 (예외 정보 로깅 가능)
            content = {'isSuccess': False, 'message': str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # 시리얼라이저의 context 설정
    def get_serializer_context(self):
        # 부모 클래스의 컨텍스트 가져오는 메소드 호출
        context = super(ChatRoomListCreateView, self).get_serializer_context()
        # 컨텍스트에 현재의 요청 객체를 추가합니다.
        context['user'] = self.kwargs.get('user_id')
        return context

    # POST 요청을 처리하여 새로운 리소스를 생성하는 메소드
    def create(self, request, *args, **kwargs):
        # 요청 데이터로부터 시리얼라이저 생성
        serializer = self.get_serializer(data=request.data)
        # 시리얼라이저의 유효성 검사 수행, 유효하지 않을 경우 예외 발생
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except ImmediateResponseException as e:
            # 즉각적인 응답이 필요할 경우 예외를 통해 응답 반환
            return e.response
        # 성공 헤더 생성
        headers = self.get_success_headers(serializer.data)
        return Response({'isSuccess': True, 'message': '요청에 성공하였습니다.',
                         'result': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    # 시리얼라이저를 통해 데이터베이스에 객체를 저장하는 메소드
    def perform_create(self, serializer):
        # 요청 데이터에서 help, helped, helper 가져옴
        help_id = self.request.data.get('help')
        help = Help.objects.get(id=help_id)

        helped = self.request.data.get('helped')

        helper_id = self.request.data.get('helper')
        helper = User.objects.get(id=helper_id)

        # 요청글의 채팅방이 이미 있는지 확인
        existing_chatroom = ChatRoom.objects.filter(
            help=help,
            helped=helped,
            helper=helper
        ).first()

        # 이미 존재하는 채팅방이 있다면 해당 채팅방의 정보를 시리얼라이즈하여 응답
        if existing_chatroom:
            serializer = ChatRoomSerializer(existing_chatroom, context={'request': self.request})
            raise ImmediateResponseException(Response(serializer.data, status=status.HTTP_200_OK))
        # 없다면 새 채팅방 객체 저장
        serializer.save(help=help, helped=helped, helper=helper)

# 채팅 메시지 목록 조회
class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer

    # GET 요청에 대한 쿼리셋을 정의하는 메소드
    def get_queryset(self):
        # URL 파라미터에서 'room_id' 값 가져옴
        room_id = self.kwargs.get('room_id')

        # room_id가 제공되지 않았을 경우, 404 Bad Request
        if not room_id:
            raise ValidationError({'isSuccess': False, 'message': 'room_id 파라미터가 필요합니다.'})

        room = ChatRoom.objects.get(id=room_id)
        user = self.request.user

        # 로그인한 유저가 채팅방 유저가 아닌 경우, 403 Forbidden
        if not (user.id == room.helped or user == room.helper):
            raise PermissionDenied({'isSuccess': False, 'message': '채팅방 이용자가 아닙니다.'})

        # {'isSuccess': True, 'message': '요청에 성공하였습니다.'} 추가가 잘 안 됨
        return Chat.objects.filter(room=room)