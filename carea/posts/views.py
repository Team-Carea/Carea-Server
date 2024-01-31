from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
import logging
# Create your views here.
def test_page(request):
    return render(request, 'posts/test_page.html')


# 카테고리별 게시물 목록을 가져오기 위한 클래스 생성
class category_list:
    def get_category(self, category):
        # DB에서 카테고리를 기준으로 값을 가져온다.
        lists = Post.objects.filter(category=category)
        # category 값이 latest, 즉 최신글인 경우 모든 게시물을 가져온다.
        if(category == 'latest') :
            lists = Post.objects.all()
        return lists
def view_category(request, category) :
    category_instance = category_list()
    category_value = category_instance.get_category(category)
    return render(request, 'category_select.html', {'category': category_value})

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
