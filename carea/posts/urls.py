from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('<int:post_id>/comments/', include('comments.urls')),
    # <bigint:post_id> = 정수형 타입의 동적 변수
    path('<int:post_id>/', views.detail, name="detail"),
    path('<str:category>/', views.category_page, name="category_page"),
    # <str:category> = 문자열 타입의 동적 변수
]
