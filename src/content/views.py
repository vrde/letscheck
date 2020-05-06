from django.shortcuts import render
from triage.models import News


MSG = """Pass it please.

Good news, Wuhan's coronavirus can be cured by one bowl of freshly boiled garlic water.
Old Chinese doctor has proven it's efficacy. Many patients have also proven this to be effective. Eight (8) cloves of chopped garlic add 7(cups) of water and bring to boil. Eat and drink the boiled garlic water, overnight improvement and heading.

Glad to share this."""


def index(request):
    all_news = News.objects.select_related('rating')
    return render(
        request, "content/index.html", {"news": all_news, "message": MSG}
    )


def how_it_works(request):
    return render(request, "content/how_it_works.html")
