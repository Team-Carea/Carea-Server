from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.categories, name="categories"),
    path('<int:post_id>/', views.detail, name="detail"),
    # <bigint:post_id> = 정수형 타입의 동적 변수
    path('<str:category>/', views.category_page, name="category_page"),
    # <str:category> = 문자열 타입의 동적 변수
]