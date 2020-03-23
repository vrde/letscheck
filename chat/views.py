from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django_q.tasks import async_task
from .forms import WhatsappMessage
from .models import Message, Media


@csrf_exempt
def inbox_whatsapp(request):
    """Webhook called by the Twilio API to deliver a message."""
    if request.method == "POST":
        form = WhatsappMessage(request.POST)
        if form.is_valid():
            message = form.save()
            for media in message.media_set.all():
                async_task("chat.tasks.download_media", media.pk)
            return HttpResponse()
        else:
            return HttpResponseBadRequest()
    else:
        raise Http404()
