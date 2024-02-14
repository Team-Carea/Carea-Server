from django.db import models
from users.models import User
# Create your models here.

# 게시물 작성
class Post(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField()
    category = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    # foreign key는 다 자동으로 뒤에 _id 붙여줘서 뺌
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
