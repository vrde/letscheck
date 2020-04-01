from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    rating = models.ForeignKey(Rating, models.SET_NULL, null=True)
    canned_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class CaseManager(models.Manager):
    def open(self):
        return (
            super()
            .get_queryset()
            .filter(response__isnull=True)
            .order_by("-request__dt")
        )


class Case(models.Model):
    request = models.OneToOneField(
        Message, on_delete=models.CASCADE, primary_key=True, related_name="case_request"
    )
    response = models.OneToOneField(
        Message, on_delete=models.CASCADE, null=True, related_name="case_response",
    )
    news = models.ForeignKey(News, null=True, on_delete=models.CASCADE)
    objects = CaseManager()


@receiver(post_save, sender=Message)
def create_case_from_new_message(sender, instance, created, **kwargs):
    if created and instance.is_incoming:
        Case.objects.create(request=instance)
