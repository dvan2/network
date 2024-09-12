from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f'{self.username}'

class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    date = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)

class Follow(models.Model):
    followed_by = models.ForeignKey(User, related_name='currently_following', on_delete=models.CASCADE)
    being_followed = models.ForeignKey(User, related_name='current_followers', on_delete=models.CASCADE)