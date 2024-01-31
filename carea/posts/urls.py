from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_page)
    # <str:category> = 문자열 타입의 동적 변수
]