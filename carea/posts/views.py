from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
import logging
# Create your views here.
def test_page(request):
    return render(request, 'posts/test_page.html')

def create(request):
    if(request.method == 'POST') :
        title = request.POST['title']
        content = request.POST['content']
        category = request.POST['category']
        #user = request.user

        # 특정 User의 ID가 1인 경우를 가정
        user_id_to_find = 1

        # 해당 User를 참조하는 MyModel 인스턴스들을 가져오는 쿼리셋
        user_info = User.objects.get(id=user_id_to_find)

        print(f"Title: {title}, Content: {content}, Category: {category},"
              f"user_id_to_find: {user_id_to_find}, post_ids: {user_info}")

        post = Post(
            title = title,
            content = content,
            category = category,
            user = user_info
        )
        post.save()
