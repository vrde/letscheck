from unittest.mock import patch, call

from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, Http404
from django.test import Client, TestCase


class TriageModelsTest(TestCase):
    def test_should_create_a_new_case_on_incoming_message(self):
        from .models import Case
        from chat.models import Message

        message = Message.objects.create(
            carrier="whatsapp",
            sender="2",
            receiver="2",
            is_incoming=True,
            body="Message body 2",
        )
        case = Case.objects.get(pk=message.pk)
        self.assertEqual(case.request.pk, message.pk)
        self.assertEqual(case.response, None)
        self.assertEqual(case.news, None)

    def test_should_not_create_a_new_case_on_outgoing_message(self):
        from .models import Case
        from chat.models import Message

        message = Message.objects.create(
            carrier="whatsapp",
            sender="2",
            receiver="2",
            is_incoming=False,
            body="Message body 2",
        )
        with self.assertRaises(ObjectDoesNotExist):
            Case.objects.get(pk=message.pk)

    def test_should_not_create_new_cases_on_multiple_saves(self):
        from .models import Case
        from chat.models import Message

        message = Message.objects.create(
            carrier="whatsapp",
            sender="2",
            receiver="2",
            is_incoming=True,
            body="Message body 2",
        )
        message.save()
        message.save()
        message.save()
        case = Case.objects.get(pk=message.pk)
        self.assertEqual(case.request.pk, message.pk)
        self.assertEqual(case.response, None)
        self.assertEqual(case.news, None)


class TriageViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.c.force_login(User.objects.get_or_create(username="testuser")[0])

    def test_index_should_display_open_cases(self):
        from .views import index
        from .models import News, Case
        from chat.models import Message

        news = News(title="title", description="description")
        news.save()
        solved_request = Message.objects.create(
            carrier="whatsapp",
            sender="1",
            receiver="1",
            is_incoming=True,
            body="Message body 1",
        )
        solved_response = Message.objects.create(
            carrier="whatsapp",
            sender="1",
            receiver="1",
            is_incoming=False,
            body="Message body 1",
        )
        solved_request.case_request.response = solved_response
        solved_request.case_request.news = news
        solved_request.case_request.save()

        new_message = Message.objects.create(
            carrier="whatsapp",
            sender="2",
            receiver="2",
            is_incoming=True,
            body="Message body 2",
        )

        response = self.c.get(reverse(index))
        cases = response.context["cases"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].request.carrier, "whatsapp")
        self.assertEqual(cases[0].request.sender, "2")
        self.assertEqual(cases[0].request.receiver, "2")
        self.assertEqual(cases[0].request.body, "Message body 2")

        self.assertContains(response, cases[0].request.sender_safe)
        self.assertContains(response, cases[0].request.dt)
        self.assertContains(response, cases[0].request.body)

    def test_case_should_display_a_case(self):
        from .views import case_details
        from .models import News, Case
        from chat.models import Message

        News.objects.create(title="title 1", description="description 1")
        News.objects.create(title="title 2", description="description 2")
        message = Message.objects.create(
            carrier="whatsapp",
            sender="1",
            receiver="1",
            is_incoming=True,
            body="Message body 1",
        )

        response = self.c.get(reverse(case_details, args=(message.pk,)))
        case = response.context["case"]
        news = response.context["news"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(news), 2)
        self.assertEqual(case.request.carrier, "whatsapp")
        self.assertEqual(case.request.sender, "1")
        self.assertEqual(case.request.receiver, "1")
        self.assertEqual(case.request.body, "Message body 1")

    @patch("triage.views.async_task")
    def test_case_should_resolve_a_case(self, mock_task):
        from .views import case_details
        from .models import News, Case
        from chat.models import Message

        news = News.objects.create(
            title="title 1",
            description="description 1",
            canned_response="canned response",
        )
        message = Message.objects.create(
            carrier="whatsapp",
            sender="1",
            receiver="2",
            is_incoming=True,
            body="Message body 1",
        )

        response = self.c.post(
            reverse(case_details, args=(message.pk,)), {"news_pk": news.pk}
        )

        message.refresh_from_db()
        self.assertEqual(message.case_request.news, news)
        self.assertEqual(message.case_request.response.carrier, "whatsapp")
        self.assertEqual(message.case_request.response.sender, "2")
        self.assertEqual(message.case_request.response.receiver, "1")
        self.assertEqual(message.case_request.response.is_incoming, False)
        self.assertEqual(message.case_request.response.body, "canned response")
        mock_task.assert_called_with(
            "chat.tasks.send_message", message.case_request.response.pk
        )


class TaskClassifyTest(TestCase):
    def setUp(self):
        from .models import News

        news = News.objects.create(
            title="Coronavirus is a bioweapon leaked from Wuhan lab",
            description="Not true",
            canned_response="fake news",
        )

    @patch("triage.tasks.async_task")
    def test_should_classify_the_demo_message(self, mock_task):
        from .models import Case
        from chat.models import Message
        from .tasks import classify

        message = Message.objects.create(
            carrier="whatsapp",
            sender="2",
            receiver="1",
            is_incoming=True,
            body="Coronavirus is bioweapon leaked from Wuhan lab",
        )
        case = Case.objects.get(pk=message.pk)
        classify(case.pk)
        case.refresh_from_db()
        response = case.response
        self.assertIsNotNone(response)
        self.assertEqual(response.carrier, "whatsapp")
        self.assertEqual(response.sender, "1")
        self.assertEqual(response.receiver, "2")
        self.assertEqual(response.is_incoming, False)
        self.assertEqual(response.body, "fake news")
        mock_task.assert_called_with("chat.tasks.send_message", response.pk)

    @patch("triage.tasks.async_task")
    def test_should_ignore_other_messages(self, mock_task):
        from .models import Case
        from chat.models import Message
        from .tasks import classify

        message = Message.objects.create(
            carrier="whatsapp",
            sender="2",
            receiver="1",
            is_incoming=True,
            body="something something coronavirus something",
        )
        case = Case.objects.get(pk=message.pk)
        classify(case.pk)
        case.refresh_from_db()
        response = case.response
        self.assertIsNone(response)
        mock_task.assert_not_called()
