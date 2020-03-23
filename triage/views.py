from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from chat.models import Message
from .models import News, MessageToNews
from .forms import NewsForm

from twilio.rest import Client


@login_required
def index(request):
    context = {
        "messages": Message.objects.prefetch_related("media_set")
        .filter(messagetonews__isnull=True)
        .order_by("-dt")
    }
    return render(request, "triage/index.html", context=context)


@login_required
def message(request, message_id):
    if request.method == "POST":
        message = Message.objects.get(id=message_id)
        news = News.objects.get(id=request.POST["news_id"])
        message_to_news = MessageToNews.objects.create(message=message, news=news)
        message_to_news.save()

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=news.canned_response,
            from_="whatsapp:+14155238886",
            to="whatsapp:{}".format(message.sender),
        )
        return HttpResponseRedirect(reverse(index))
    else:
        context = {
            "message": Message.objects.get(id=message_id),
            "news": News.objects.all(),
        }
    return render(request, "triage/message.html", context=context)


@login_required
def create(request, message_id):
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(message, args=[message_id]))
    else:
        form = NewsForm()
    context = {
        "message": Message.objects.get(id=message_id),
        "news": News.objects.all(),
        "form": form,
    }
    return render(request, "triage/create.html", context=context)
