from django.db import models
from django.contrib.auth.models import User
from chat.models import Message


class Rating(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    rating = models.ForeignKey(Rating, models.SET_NULL, blank=True, null=True)
    canned_response = models.TextField()

    def __str__(self):
        return self.title


class MessageToNews(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE, primary_key=True)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
