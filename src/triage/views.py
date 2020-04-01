from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from django_q.tasks import async_task

from chat.models import Message
from chat.tasks import send_message
from .models import News, Case
from .forms import NewsForm


@login_required
def index(request):
    context = {"cases": Case.objects.open().select_related("request")}
    return render(request, "triage/index.html", context=context)


@login_required
def case_details(request, case_pk):
    if request.method == "POST":
        case = Case.objects.get(pk=case_pk)
        news = News.objects.get(pk=request.POST["news_pk"])
        # TODO send error message
        assert news.canned_response
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
        async_task("chat.tasks.send_message", message_response.pk)
        return HttpResponseRedirect(reverse(index))
    else:
        context = {
            "case": Case.objects.select_related("request").get(pk=case_pk),
            "news": News.objects.all(),
        }
    return render(request, "triage/case_details.html", context=context)


@login_required
def create(request, message_pk):
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
