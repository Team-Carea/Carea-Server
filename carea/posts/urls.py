from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.write_post, name="write_post"),
    path('<str:category>/', views.view_category, name="view_category")
    # <str:category> = 문자열 타입의 동적 변수
]