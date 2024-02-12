from django.db import models

from users.models import User

class Post(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField()
    category = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    user_info = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
