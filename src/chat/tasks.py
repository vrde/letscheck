import os
import shutil
from tempfile import NamedTemporaryFile
from hashlib import sha256

import requests
from twilio.rest import Client

from django.conf import settings
from django.utils.timezone import now
from .models import Media, Message

CHUNK_SIZE = 1024 * 1024


def download_media(media_pk):
    media = Media.objects.get(pk=media_pk)
    r = requests.get(media.twilio_media_url, stream=True)
    f = NamedTemporaryFile(delete=False)
    h = sha256()
    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
        # FIXME: should I check if chunk has data?
        f.write(chunk)
        h.update(chunk)
    f.close()
    shutil.move(f.name, os.path.join(settings.MEDIA_ROOT, h.hexdigest()))
    media.content_hash = h.hexdigest()
    media.save()


def send_message(message_pk, anonymize=True):
    message = Message.objects.get(pk=message_pk)
    if message.sender == settings.SULLA_SENDER:
        requests.post(
            settings.SULLA_API_ENDPOINT,
            data={"recipient": message.receiver, "body": message.body},
        )
        message.twilio_account_sid = "sulla"
        message.twilio_message_sid = "sulla"
    else:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        response = client.messages.create(
            body=message.body,
            from_=":".join([message.carrier, message.sender]),
            to=":".join([message.carrier, message.receiver]),
        )
        message.twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        message.twilio_message_sid = response.sid
    if anonymize:
        message.receiver = ""
    message.dt = now()
    message.save()
