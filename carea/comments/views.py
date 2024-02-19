from comments.models import Comment
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CommentSerializer


# 댓글 리스트 출력을 위한 클래스
class CommentInfo:
    def view_comment(self, post_id):
        comment_list = Comment.objects.filter(post=post_id).order_by('-created_at')
        return comment_list

@api_view(['GET', 'POST'])
def comment(request, post_id) :
    comment_instance = CommentInfo()
    comments_list = comment_instance.view_comment(post_id)
    comments_serializer = CommentSerializer(comments_list, many=True)


    # 댓글 리스트 출력
    if (request.method == "GET"):
        if (comments_serializer.data is not None) :
            return Response({
                "isSuccess" : True,
                "message" : "댓글 출력에 성공하였습니다.",
                "result" : comments_serializer.data
            }, status=200)
        else :
            return Response({
                "isSuccess" : False,
                "message" : "댓글이 존재하지 않습니다."
            }, status=404)

    # 댓글 작성
    if (request.method == "POST"):
        # 헤더에서 받은 토큰으로 유저 불러오기
        user = request.user

        write_serializer = CommentSerializer(data=request.data)
        if write_serializer.is_valid() :
            write_serializer.save(post_id=post_id, user=user)
            return Response({
                "isSuccess" : True,
                "message" : "댓글이 등록되었습니다.",
                "result": comments_serializer.data
            }, status=201)
        else:
            return Response({
                "isSuccess" : False,
                "message": "댓글을 입력하세요.",
                "errors": write_serializer.errors
            }, status=400)