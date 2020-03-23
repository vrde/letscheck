import os
import shutil
from tempfile import NamedTemporaryFile
from hashlib import sha256
import requests
from django.conf import settings
from .models import Media

CHUNK_SIZE = 1024 * 1024


def download_media(media_id):
    media = Media.objects.get(id=media_id)
    r = requests.get(media.url, stream=True)
    f = NamedTemporaryFile(delete=False)
    h = sha256()
    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
        # FIXME: should I check if chunk has data?
        f.write(chunk)
        h.update(chunk)
    f.close()
    shutil.move(f.name, os.path.join(settings.LETSCHECK_MEDIA_DIR, h.hexdigest()))
    media.content_hash = h.hexdigest()
    media.save()
