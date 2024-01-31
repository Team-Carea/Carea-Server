from django.db import models

# Create your models here.
class User(models.Model):
    nickname = models.CharField(max_length=10)
    email = models.CharField(max_length=20)
    profile_url = models.CharField(max_length=255, blank=True, null=True)
    introduction = models.CharField(max_length=100, blank=True, null=True)
    point = models.IntegerField(default=0)
    token = models.CharField(max_length=255, blank=True, null=True)