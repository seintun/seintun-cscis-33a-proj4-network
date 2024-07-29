import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    content = models.TextField(max_length=120)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.id}: {self.user} created #{self.id} {str(self.content)[:25]} on ({str(self.timestamp)})"


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    user_follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_follower"
    )

    def __str__(self):
        return f"{self.user} follows {self.user_follower}"
