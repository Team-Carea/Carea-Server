from django.db import models

from helps.models import Help
from users.models import User

class ChatRoom(models.Model):
    help = models.ForeignKey(Help, on_delete=models.PROTECT)
    helped = models.IntegerField()   # 도움 요청자 id
    helper = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)

class Chat(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    message = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message