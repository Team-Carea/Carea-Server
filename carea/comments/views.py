from comments.models import Comment
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CommentSerializer

# Create your views here.

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
        return Response({
            "message" : "댓글 출력에 성공하였습니다.",
            "data" : comments_serializer.data
        }, status=201)

    # 댓글 작성
    if (request.method == "POST"):
        write_serializer = CommentSerializer(data=request.data)
        if write_serializer.is_valid() :
            write_serializer.save()
            return Response({
                "message" : "댓글 작성에 성공하였습니다.",
                "data": comments_serializer.data
            }, status=201)
        else:
            return Response({
                "message": "댓글 작성에 실패하였습니다.",
                "errors": write_serializer.errors
            }, status=404)