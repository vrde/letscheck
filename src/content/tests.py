from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client, TestCase


class ContentViewTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_index_should_display_news(self):
        from .views import index
        from triage.models import News, Rating, Case
        from chat.models import Message

        rating = Rating.objects.create(name="rating1")

        news = News.objects.create(
            title="title1",
            description="description1",
            rating=rating)

        message_1 = Message.objects.create(
            carrier="whatsapp",
            sender="1",
            receiver="1",
            is_incoming=True,
            body="Message body 1",
        )
        message_2 = Message.objects.create(
            carrier="whatsapp",
            sender="2",
            receiver="2",
            is_incoming=False,
            body="Message body 2",
        )
        message_3 = Message.objects.create(
            carrier="whatsapp",
            sender="3",
            receiver="3",
            is_incoming=True,
            body="Message body 3",
        )
        message_4 = Message.objects.create(
            carrier="whatsapp",
            sender="4",
            receiver="4",
            is_incoming=False,
            body="Message body 4",
        )
        
        case_1 = Case.objects.get(pk=message_1.pk)
        case_1.response = message_2
        case_1.news = news
        case_1.save()

        case_2 = Case.objects.get(pk=message_3.pk)
        case_2.response = message_4
        case_2.news = news
        case_2.save()
        
        response = self.c.get(reverse(index))
        displayed_news = response.context["news"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(displayed_news), 1)
        self.assertEqual(displayed_news[0].title, "title1")
        self.assertEqual(displayed_news[0].description, "description1")
        self.assertEqual(displayed_news[0].rating.name, "rating1")
        self.assertEqual(displayed_news[0].cases, 2)
