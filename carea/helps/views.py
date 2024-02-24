import googlemaps
import json

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import HelpSerializer, MainHelpSerializer, DetailHelpSerializer
from .models import Help
from chats.models import ChatRoom

def stt(request):
    return render(request, 'stt.html')

class Map():
    def view_helps(self):
        help_list = Help.objects.all()
        return help_list

    def geocode(self,address):
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        geocode_result = json.dumps(gmaps.geocode(address))
        result = json.loads(geocode_result)
        latitude = result[0]['geometry']['location']['lat']
        longitude = result[0]['geometry']['location']['lng']
        return latitude, longitude

    def help_detail(self, help_id):
        help_info = get_object_or_404(Help, pk=help_id)
        return help_info


@api_view(['GET', 'POST'])
def maps(request):
    help_instance = Map()

    if (request.method == 'GET'):
        help_list = help_instance.view_helps()
        helps_serializer = MainHelpSerializer(help_list, many=True)

        if(helps_serializer is not None) :
            return Response({
                "isSuccess" : True,
                "message" : "요청글 출력에 성공하였습니다.",
                "result" : helps_serializer.data
            }, status=200)

        else :
            return Response({
                "isSuccess" : False,
                "message" : "요청글을 찾을 수 없습니다."
            }, status=404)


    elif (request.method == 'POST'):
        # 헤더에서 받은 토큰으로 유저 불러오기
        user = request.user
        # 주소값을 받아서 위도 경도로 변환
        lat, lng = help_instance.geocode(request.data['location'])
        write_serializer = HelpSerializer(data=request.data)

        if (write_serializer.is_valid()):
            write_serializer.save(user=user, latitude=lat, longitude=lng)
            return Response({
                "isSuccess" : True,
                "message" : "요청글이 등록되었습니다.",
                "result" : write_serializer.data
            }, status=201)

        else:
            return Response({
                "isSuccess" : False,
                "message" : "요청글을 입력하세요."
            }, status=400)

# 상세 요청글 출력
@api_view(['GET'])
def helps(request, help_id):

    if (request.method == 'GET'):
        help_instance = Map()
        help_info = help_instance.help_detail(help_id)
        help_serializer = DetailHelpSerializer(help_info)

        if (help_serializer is not None):
            return Response({
                "isSuccess" : True,
                "message" : "요청글 정보 출력에 성공했습니다.",
                "result" : help_serializer.data
            }, status=200)

        else:
            return Response({
                "isSuccess" : False,
                "message" : "요청글을 찾을 수 없습니다."
            }, status=404)

# 도움 요청자/제공자 판별
@api_view(['GET'])
def identify(request, room_id):

    if (request.method == 'GET') :
        # 헤더에서 받은 토큰으로 유저 불러오기
        user = request.user

        try:
            # 채팅방 인스턴스 불러오기
            room = ChatRoom.objects.get(id=room_id)
        except Exception:
            return Response({
                "isSuccess": False,
                "message": "채팅방을 찾을 수 없습니다.",
            }, status=404)

        if (user != room.helper) and (user.id != room.helped):
            return Response({
                "isSuccess": False,
                "message": "채팅방 참여자가 아닙니다.",
            }, status=403)

        # 유저가 채팅방에서 어떤 역할인지 판단
        if user.id == room.helped:
            role = "seeker"
        else:
            role = "helper"

        return Response({
            "isSuccess": True,
            "message": "요청에 성공하였습니다.",
            "result": role
        }, status=200)

# 도움 인증 완료 시 경험치 증가
@api_view(['PATCH'])
def increase_points(request, room_id):

    if (request.method == 'PATCH') :
        # 헤더에서 받은 토큰으로 유저 불러오기
        user = request.user

        try:
            # 채팅방 인스턴스 불러오기
            room = ChatRoom.objects.get(id=room_id)
        except Exception:
            return Response({
                "isSuccess": False,
                "message": "채팅방을 찾을 수 없습니다.",
            }, status=404)

        if (user != room.helper) and (user.id != room.helped):
            return Response({
                "isSuccess": False,
                "message": "채팅방 참여자가 아닙니다.",
            }, status=403)

        # 도움 요청자 +5, 도움 제공자 +10
        if user.id == room.helped:
            points = 5
        else:
            points = 10

        user.point += points
        user.save()

        return Response({
            "isSuccess": True,
            "message": "요청에 성공하였습니다.",
            "result": {
                "increased_points": points,
                "user_points": user.point,
            }
        }, status=200)