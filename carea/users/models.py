from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
# Create your models here.
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=10)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    objects = UserManager()

    # 필요한 필드 추가
    profile_url = models.CharField(max_length=255, blank=True, null=True)
    introduction = models.CharField(max_length=100, blank=True, null=True)
    point = models.IntegerField(default=0)

    def __str__(self):
        return self.email