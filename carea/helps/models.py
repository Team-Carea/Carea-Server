from django.db import models
from users.models import User

class Help(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    location = models.CharField(max_length=255, default="")
    latitude = models.DecimalField(max_digits=15, decimal_places=12, default=0.0)
    longitude = models.DecimalField(max_digits=15, decimal_places=12, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
