from django.shortcuts import render
from triage.models import News


def index(request):
    all_news = News.objects.all()
    return render(request, "content/index.html", {"news": News.objects.all()})
