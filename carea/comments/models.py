from django.db import models

from posts.models import Post
from users.models import User

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    content = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
