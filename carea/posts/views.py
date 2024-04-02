from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CategoryPostSerializer,PostSerializer
from .models import Post
from users.models import User



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

@api_view(['GET', 'POST'])
#카테고리 내의 게시물을 보여줌.
def category_page(request, category) :
    category_instance = CategoryInfo()
    category_posts = category_instance.get_category_list(category)

    posts_serializer = CategoryPostSerializer(category_posts, many=True)

    #카테고리 목록
    categories = ['latest', 'free', 'economic', 'life', 'future']

    # 요청이 GET인 경우 : 카테고리에 해당하는 게시물들을 보여줌.
    if request.method == 'GET' :
        if (category in categories) :
            return Response({
                "isSuccess" : True,
                "message" : "해당 카테고리의 게시물 출력에 성공했습니다.",
                "result" : posts_serializer.data
            }, status=200)
        # 카테고리 값이 아닌 값이라면
        else :
            return Response({
                "isSuccess" : False,
                "message" : "해당 카테고리 값을 찾을 수 없습니다."
            }, status=404)

    # 요청이 POST인 경우 게시글을 작성하도록 함.
    elif request.method == "POST":
        # 헤더에서 받은 토큰으로 유저 불러오기
        user = request.user

        write_serializer = PostSerializer(data=request.data)
        if write_serializer.is_valid():
            # 특정 게시판 내에서는 카테고리 선택을 할 수 없음
            if(category == "latest") :
                write_serializer.save(category=request.data['category'], user=user)
            else :
                write_serializer.save(category=category, user=user)
                
            return Response({
                "isSuccess" : True,
                "message" : "게시물이 등록되었습니다.",
                "result" : posts_serializer.data
            }, status=201)

        else:
            return Response({
                "isSuccess" : False,
                "message": "제목/내용을 입력하세요."
            }, status=400)


# 게시물 상세 보기 기능을 위한 클래스
class PostDetail:
    # 게시물의 포스트 아이디 받아오기
    def get_post_info(self, pk):
        detail_info = get_object_or_404(Post, id=pk)
        return detail_info

# 포스트 아이디를 통해 게시물의 상세정보 전달
@api_view(['GET', 'POST'])
def detail(request, post_id):
    detail_instance = PostDetail()
    post_detail = detail_instance.get_post_info(post_id)
    detail_serializer = PostSerializer(post_detail)

    # 요청이 GET인 경우 게시물의 상세 정보 출력 및 댓글 출력
    if request.method == "GET" :
        if post_detail is not None:
            return Response({
                "isSuccess" : True,
                "message" : "상세 정보 출력에 성공했습니다.",
                "result" : detail_serializer.data
            }, status=200)
        else:
            return Response({
                "isSuccess" : False,
                "message" : "해당 게시물이 없습니다."
            }, status=404)