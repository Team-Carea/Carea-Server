from django.urls import path
from . import views

urlpatterns = [
    path('', views.home), # 빈 경로 -> 홈 화면
    path('logout', views.logout_view)
]
