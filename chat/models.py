from urllib.parse import urljoin
from django.conf import settings
from django.db import models


class Message(models.Model):
    carrier = models.CharField(max_length=100)
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    body = models.TextField()
    dt = models.DateTimeField(auto_now_add=True)

    def sender_safe(self):
        return self.sender[:3] + (len(self.sender) - 3) * "•"

    def __str__(self):
        return "{}: {}".format(self.sender, self.body[:255])


class Media(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    url = models.CharField(max_length=1024)
    content_type = models.CharField(max_length=64)
    content_hash = models.CharField(max_length=64, null=True)

    @property
    def embed_as(self):
        if self.content_type.startswith("image"):
            return "image"

    @property
    def url(self):
        return urljoin(settings.MEDIA_URL, self.content_hash)
