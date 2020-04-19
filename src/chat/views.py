from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django_q.tasks import async_task
from .decorators import validate_twilio_or_sulla_request
from .forms import WhatsappMessage
from .models import Message, Media


@require_POST
@csrf_exempt
@validate_twilio_or_sulla_request
def inbox_whatsapp(request):
    """Webhook called by the Twilio API to deliver a message."""
    form = WhatsappMessage(request.POST)
    if form.is_valid():
        message = form.save()
        for media in message.media_set.all():
            async_task("chat.tasks.download_media", media.pk)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
