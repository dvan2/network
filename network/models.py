from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.PositiveIntegerField(default=0)
    following = models.PositiveIntegerField(default=0)

class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    date = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)