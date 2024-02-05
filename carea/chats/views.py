from django.shortcuts import render
from django.http import Http404

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .serializers import ChatRoomSerializer, ChatSerializer
from .models import ChatRoom, Chat

def index(request):
    return render(request, "chat/index.html")

def room(request, room_id):
    return render(request, "chat/room.html", {"room_id": room_id})


# 사용자 정의 예외 클래스, 예외 발생 시 즉각적인 HTTP 응답을 위해 사용됩니다.
class ImmediateResponseException(Exception):
    # 예외 인스턴스를 생성할 때 HTTP 응답 객체를 받습니다.
    def __init__(self, response):
        self.response = response

# 채팅방 생성
@api_view(['POST'])
def chat_start(request):
    serializer = ChatRoomSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        # 성공 여부랑 메시지 붙여서 내보내기
        return Response(serializer.data)

    # 채팅방 이미 있는 경우 (ChatRoom애서 helped_id랑 helper 검색)
    return Response({"isSuccess": False, "message": "요청에 실패하였습니다."})

# 채팅방 목록 조회 및 생성
class ChatRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer

    # GET 요청에 대한 쿼리셋을 정의하는 메소드
    def get_queryset(self):
        try:
            # 요청의 path variable에서 'user_id' 값을 가져옵니다.
            user_id = self.kwargs.get('user_id')

            # user_id 파라미터가 없으면 ValidationError 예외를 발생시킵니다.
            if not user_id:
                raise ValidationError('user_id 파라미터가 필요합니다.')

            # 채팅방 객체를 필터링하여, 해당 id를 가진 사용자가 속한 채팅방을 찾습니다.
            return ChatRoom.objects.filter(
                helped=user_id
            ) | ChatRoom.objects.filter(
                helper=user_id
            )

        except ValidationError as e:
            # ValidationError 발생 시, 상태 코드 400과 함께 에러 상세 정보를 반환합니다.
            content = {'detail': e.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 다른 종류의 예외 발생 시, 상태 코드 400과 함께 에러 상세 정보를 반환합니다.
            # 여기에서 예외 정보를 로깅할 수 있습니다.
            content = {'detail': str(e)}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    # POST 요청을 처리하여 새로운 리소스를 생성하는 메소드입니다.
    def create(self, request, *args, **kwargs):
        # 요청 데이터로부터 시리얼라이저를 생성합니다.
        serializer = self.get_serializer(data=request.data)
        # 시리얼라이저의 유효성 검사를 수행합니다. 유효하지 않을 경우 예외가 발생합니다.
        serializer.is_valid(raise_exception=True)
        try:
            # 시리얼라이저를 통해 데이터 저장을 수행합니다.
            self.perform_create(serializer)
        except ImmediateResponseException as e:
            # 즉각적인 응답이 필요할 경우 예외를 통해 응답을 반환합니다.
            return e.response
        # 성공 헤더를 생성합니다.
        headers = self.get_success_headers(serializer.data)
        # 상태 코드 201를 반환하며 새로 생성된 데이터를 응답합니다.
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 시리얼라이저를 통해 데이터베이스에 객체를 저장하는 메소드입니다.
    def perform_create(self, serializer):
        # 요청 데이터에서 helped_id와 helper_id를 가져옵니다.
        help = self.request.data.get('help')
        helped = self.request.data.get('helped')
        helper = self.request.data.get('helper')
        # 요청글의 채팅방이 이미 있는지 확인합니다.
        existing_chatroom = ChatRoom.objects.filter(
            help=help,
            helped=helped,
            helper=helper).first()

        # 이미 존재하는 채팅방이 있다면 해당 채팅방의 정보를 시리얼라이즈하여 응답합니다.
        if existing_chatroom:
            serializer = ChatRoomSerializer(existing_chatroom, context={'request': self.request})
            raise ImmediateResponseException(Response(serializer.data, status=status.HTTP_200_OK))
        # 새 채팅방 객체를 저장합니다.
        serializer.save(help=help, helped=helped, helper=helper)

# 채팅 메시지 목록 조회
class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer

    # GET 요청에 대한 쿼리셋을 정의하는 메소드
    def get_queryset(self):
        # URL 파라미터에서 'room_id' 값을 가져옵니다.
        room_id = self.kwargs.get('room_id')

        # room_id가 제공되지 않았을 경우 에러 메시지와 함께 400 상태 코드 응답을 반환합니다.
        if not room_id:
            content = {'detail': 'room_id 파라미터가 필요합니다.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # room_id에 해당하는 메시지 객체들을 쿼리셋으로 가져옵니다.
        queryset = Chat.objects.filter(room=room_id)

        # 해당 room_id의 메시지가 존재하지 않을 경우 404 Not Found 예외를 발생시킵니다.
        if not queryset.exists():
            raise Http404('해당 room_id로 메시지를 찾을 수 없습니다.')

        # 쿼리셋을 반환합니다.
        return queryset