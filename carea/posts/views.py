from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Post
from users.models import User
# Create your views here.


# 카테고리 별 게시물 목록과 카테고리 값 자체를 가져오기 위한 클래스
class CategoryInfo:

    # 카테고리 내 모든 게시물
    def get_category_list(self, category):
        # DB에서 카테고리를 기준으로 값을 가져온다.
        lists = Post.objects.filter(category=category).order_by('-created_at')
        # category 값이 latest, 즉 최신글인 경우 모든 게시물을 가져온다.
        if(category == 'latest') :
            lists = Post.objects.all().order_by('-created_at')
        return lists

    # 카테고리 단일 값
    def get_category_value(self, category):
        return category

def view_category(request, category) :
    category_instance = CategoryInfo()
    category_posts = category_instance.get_category_list(category)
    # 게시물 작성 페이지에서 카테고리 목록 페이지로 돌아오기 위함
    global g_category_value
    g_category_value = category_instance.get_category_value(category)
    return render(request, 'category_select.html', {'category': category_posts, 'g_category_value': g_category_value})

# 게시물 작성을 위한 클래스 생성
class Write:
    # 게시물 작성 페이지 출력
    def view_write_page(self, request):
        return render(request, 'post.html')

    # 게시물 정보를 DB에 저장
    def save_post_info(self, request):
        # 임의로 user_id를 3로 설정
        user_id = 3
        Post.objects.create(
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            category=request.POST.get('category'),
            user=User.objects.get(id=user_id)
        )

def write_post(request):
    post_instance = Write()
    if request.method == "POST":
        post_instance.save_post_info(request)
        # 이전 페이지로 돌아가기
        return view_category(request, g_category_value)
    else:
        return post_instance.view_write_page(request)
    # 게시물 상세 보기 기능을 위한 클래스
class PostDetail:
    # 게시물의 포스트 아이디 받아오기
    def get_post_info(self, pk):
        detail_info = get_object_or_404(Post, id=pk)
        return detail_info

# 포스트 아이디를 통해 게시물의 상세정보 전달
def view_detail(request, post_id):
    detail_instance = PostDetail()
    post_detail = detail_instance.get_post_info(post_id)
    return render(request, 'post_detail.html', {'detail': post_detail})