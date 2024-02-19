from django.shortcuts import render
import googlemaps
import json
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .serializers import HelpSerializer, MainHelpSerializer, DetailHelpSerializer
from .models import Help

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


@api_view(['GET','POST'])
def maps(request):
    help_instance = Map()

    if(request.method=='GET'):
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


    elif(request.method=='POST'):
        # 헤더에서 받은 토큰으로 유저 불러오기
        user = request.user
        # 주소값을 받아서 위도 경도로 변환
        lat, lng = help_instance.geocode(request.data['location'])
        write_serializer = HelpSerializer(data=request.data)

        if(write_serializer.is_valid()):
            write_serializer.save(user=user, latitude=lat, longitude=lng)
            return Response({
                "isSuccess" : True,
                "message" : "요청글이 등록되었습니다.",
                "result" : write_serializer.data
            }, status=201)

        else :
            return Response({
                "isSuccess" : False,
                "message" : "요청글을 입력하세요."
            }, status=400)

# 상세 요청글 출력
@api_view(['GET'])
def helps(request, help_id):

    if(request.method == 'GET') :
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
