from django.db import models
from django.contrib.auth.models import User


class AIQuery(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    language = models.CharField(max_length=50)

    prompt = models.TextField()

    response = models.TextField()

    is_favorite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.user.username


class Activity(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    action = models.CharField(max_length=255)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.action