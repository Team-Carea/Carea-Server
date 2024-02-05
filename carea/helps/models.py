from django.db import models

from users.models import User

class Help(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    title = models.CharField(max_length=20)
    content = models.TextField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
