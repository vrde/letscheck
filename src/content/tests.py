from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client, TestCase


class ContentViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.c.force_login(User.objects.get_or_create(username="testuser")[0])

    def test_index_should_display_news(self):
        from .views import index
        from triage.models import News, Rating

        rating = Rating(name="rating1")
        rating.save()

        news = News(
            title="title1",
            description="description1",
            rating=rating)
        news.save()

        response = self.c.get(reverse(index))
        displayed_news = response.context["news"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(displayed_news), 1)
        self.assertEqual(displayed_news[0].title, "title1")
        self.assertEqual(displayed_news[0].description, "description1")
        self.assertEqual(displayed_news[0].rating.name, "rating1")
