from django.db import models
from users.models import User
from posts.models import Post
# Create your models here.
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    content = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)