import os
import shutil
from tempfile import NamedTemporaryFile
from hashlib import sha256

import requests

from django.conf import settings
from .models import News, Case
from chat.models import Media, Message
from django_q.tasks import async_task


def classify(case_pk):
    case = Case.objects.get(pk=case_pk)
    news = News.objects.filter(title__icontains="garlic").first()
    body = case.request.body.lower()

    if not news or not news.canned_response:
        return

    if "garlic" in body and "coronavirus" in body:
        message_response = Message.objects.create(
            carrier=case.request.carrier,
            sender=case.request.receiver,
            receiver=case.request.sender,
            body=news.canned_response,
            is_incoming=False,
        )
        case.news = news
        case.response = message_response
        case.save()
        case.request.sender = ""
        case.request.save()
        async_task("chat.tasks.send_message", message_response.pk)
