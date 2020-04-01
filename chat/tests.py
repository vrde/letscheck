from unittest.mock import patch, call, Mock, PropertyMock

from django.urls import reverse
from django.utils.timezone import now
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.http import HttpResponseBadRequest, Http404


class InboxWhatsappTest(TestCase):
    def setUp(self):
        self.c = Client()

    @override_settings(DEBUG=True)
    @patch("chat.views.async_task")
    def test_should_process_simple_message(self, mock_task):
        from .views import inbox_whatsapp
        from .models import Message, Media

        response = self.c.post(
            reverse(inbox_whatsapp),
            {
                "AccountSid": "AC00000000000000000000000000000000",
                "ApiVersion": "2010-04-01",
                "Body": "Hello, World!",
                "From": "whatsapp:+4911111111111",
                "MessageSid": "SM00000000000000000000000000000000",
                "NumMedia": "0",
                "NumSegments": "1",
                "SmsMessageSid": "SM00000000000000000000000000000000",
                "SmsSid": "SM00000000000000000000000000000000",
                "SmsStatus": "received",
                "To": "whatsapp:+11111111111",
            },
        )
        self.assertEqual(response.status_code, 200)
        messages = Message.objects.filter(sender__exact="+4911111111111")
        self.assertEqual(messages.count(), 1)
        message = messages.first()
        self.assertEqual(message.carrier, "whatsapp")
        self.assertEqual(message.sender, "+4911111111111")
        self.assertEqual(message.receiver, "+11111111111")
        self.assertEqual(message.is_incoming, True)
        self.assertEqual(
            message.twilio_account_sid, "AC00000000000000000000000000000000"
        )
        self.assertEqual(
            message.twilio_message_sid, "SM00000000000000000000000000000000"
        )
        self.assertEqual(message.media_set.count(), 0)
        mock_task.assert_not_called()

    @override_settings(DEBUG=True)
    @patch("chat.views.async_task")
    def test_should_process_message_with_media_without_body(self, mock_task):
        from .views import inbox_whatsapp
        from .models import Message, Media

        response = self.c.post(
            reverse(inbox_whatsapp),
            {
                "AccountSid": "AC00000000000000000000000000000000",
                "ApiVersion": "2010-04-01",
                "From": "whatsapp:+4911111111111",
                "MessageSid": "SM00000000000000000000000000000000",
                "NumMedia": "2",
                "NumSegments": "1",
                "MediaContentType0": "application/pdf",
                "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/0",
                "MediaContentType1": "image/png",
                "MediaUrl1": "https://api.twilio.com/2010-04-01/Accounts/1",
                "SmsMessageSid": "SM00000000000000000000000000000000",
                "SmsSid": "SM00000000000000000000000000000000",
                "SmsStatus": "received",
                "To": "whatsapp:+11111111111",
            },
        )
        self.assertEqual(response.status_code, 200)
        messages = Message.objects.filter(sender__exact="+4911111111111")
        self.assertEqual(messages.count(), 1)
        message = messages.first()
        self.assertEqual(message.carrier, "whatsapp")
        self.assertEqual(message.sender, "+4911111111111")
        self.assertEqual(message.receiver, "+11111111111")
        self.assertEqual(message.is_incoming, True)
        self.assertEqual(
            message.twilio_account_sid, "AC00000000000000000000000000000000"
        )
        self.assertEqual(
            message.twilio_message_sid, "SM00000000000000000000000000000000"
        )
        self.assertEqual(message.media_set.count(), 2)
        media = message.media_set.all()
        self.assertEqual(media[0].content_type, "application/pdf")
        self.assertEqual(
            media[0].twilio_media_url, "https://api.twilio.com/2010-04-01/Accounts/0"
        )
        self.assertEqual(media[1].content_type, "image/png")
        self.assertEqual(
            media[1].twilio_media_url, "https://api.twilio.com/2010-04-01/Accounts/1"
        )
        mock_task.assert_has_calls(
            [
                call().async_task("chat.tasks.download_media", media[0].pk),
                call().async_task("chat.tasks.download_media", media[1].pk),
            ]
        )

    @override_settings(DEBUG=True)
    @patch("chat.views.async_task")
    def test_should_process_message_with_media(self, mock_task):
        from .views import inbox_whatsapp
        from .models import Message, Media

        response = self.c.post(
            reverse(inbox_whatsapp),
            {
                "AccountSid": "AC00000000000000000000000000000000",
                "ApiVersion": "2010-04-01",
                "Body": "Hello, World!",
                "From": "whatsapp:+4911111111111",
                "MessageSid": "SM00000000000000000000000000000000",
                "NumMedia": "2",
                "NumSegments": "1",
                "MediaContentType0": "application/pdf",
                "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/0",
                "MediaContentType1": "image/png",
                "MediaUrl1": "https://api.twilio.com/2010-04-01/Accounts/1",
                "SmsMessageSid": "SM00000000000000000000000000000000",
                "SmsSid": "SM00000000000000000000000000000000",
                "SmsStatus": "received",
                "To": "whatsapp:+11111111111",
            },
        )
        self.assertEqual(response.status_code, 200)
        messages = Message.objects.filter(sender__exact="+4911111111111")
        self.assertEqual(messages.count(), 1)
        message = messages.first()
        self.assertEqual(message.carrier, "whatsapp")
        self.assertEqual(message.sender, "+4911111111111")
        self.assertEqual(message.receiver, "+11111111111")
        self.assertEqual(message.is_incoming, True)
        self.assertEqual(
            message.twilio_account_sid, "AC00000000000000000000000000000000"
        )
        self.assertEqual(
            message.twilio_message_sid, "SM00000000000000000000000000000000"
        )
        self.assertEqual(message.media_set.count(), 2)
        media = message.media_set.all()
        self.assertEqual(media[0].content_type, "application/pdf")
        self.assertEqual(
            media[0].twilio_media_url, "https://api.twilio.com/2010-04-01/Accounts/0"
        )
        self.assertEqual(media[1].content_type, "image/png")
        self.assertEqual(
            media[1].twilio_media_url, "https://api.twilio.com/2010-04-01/Accounts/1"
        )
        mock_task.assert_has_calls(
            [
                call().async_task("chat.tasks.download_media", media[0].pk),
                call().async_task("chat.tasks.download_media", media[1].pk),
            ]
        )

    @override_settings(DEBUG=True)
    @patch("django_q.tasks.async_task")
    def test_should_reject_messages_with_wrong_number_of_media(self, mock_task):
        from .views import inbox_whatsapp
        from .models import Message, Media

        response = self.c.post(
            reverse(inbox_whatsapp),
            {
                "AccountSid": "AC00000000000000000000000000000000",
                "ApiVersion": "2010-04-01",
                "Body": "Hello, World!",
                "From": "whatsapp:+4911111111111",
                "MessageSid": "SM00000000000000000000000000000000",
                "NumMedia": "2",
                "NumSegments": "1",
                "MediaContentType0": "application/pdf",
                "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/0",
                "SmsMessageSid": "SM00000000000000000000000000000000",
                "SmsSid": "SM00000000000000000000000000000000",
                "SmsStatus": "received",
                "To": "whatsapp:+11111111111",
            },
        )
        self.assertEqual(response.status_code, 400)
        messages = Message.objects.filter(sender__exact="+4911111111111")
        self.assertEqual(messages.count(), 0)
        mock_task.assert_not_called()


class TaskDownloadMediaTest(TestCase):
    MOCK_CHUNKS = [b"one", b"two", b"three"]

    class MockResponse:
        def __init__(self, chunks):
            self.chunks = chunks

        def iter_content(self, *args, **kwargs):
            for chunk in self.chunks:
                yield chunk

    @patch("chat.tasks.NamedTemporaryFile")
    @patch("requests.get", return_value=MockResponse(MOCK_CHUNKS))
    @patch("shutil.move")
    def test_should_download_the_file_calculate_sha_and_store(
        self, mock_move, mock_response, mock_temp_file
    ):
        from hashlib import sha256
        from .models import Message, Media
        from .tasks import download_media

        mock_temp_file.name.return_value = "tempname"

        h = sha256()
        h.update(b"".join(self.MOCK_CHUNKS))

        message = Message.objects.create(
            carrier="test",
            sender="test",
            receiver="test",
            is_incoming=True,
            body="test",
        )
        media = message.media_set.create(
            twilio_media_url="http://example.com/media.txt", content_type="text"
        )
        download_media(media.pk)
        mock_temp_file.assert_has_calls(
            [
                call()(delete=False),
                call().write(b"one"),
                call().write(b"two"),
                call().write(b"three"),
                call().close(),
            ]
        )
        mock_move.assert_called_once()
        media.refresh_from_db()
        self.assertEqual(media.content_hash, h.hexdigest())


class TaskSendMessageTest(TestCase):
    @patch("chat.tasks.Client")
    @patch("chat.tasks.now", return_value=now())
    def test_should_send_the_message_and_update_sid_dt(self, mock_now, mock_client):
        from .models import Message
        from .tasks import send_message
        from django.conf import settings

        mock_client_instance = Mock()
        mock_client_instance.messages.create.return_value = Mock(
            sid="XXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )
        mock_client.return_value = mock_client_instance

        message = Message.objects.create(
            carrier="whatsapp",
            sender="1",
            receiver="2",
            is_incoming=False,
            body="test",
        )

        send_message(message.pk)
        mock_client.assert_called_with(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )
        mock_client_instance.messages.create.assert_called_with(
            body="test", from_="whatsapp:1", to="whatsapp:2",
        )
        message.refresh_from_db()
        self.assertEqual(message.twilio_account_sid, settings.TWILIO_ACCOUNT_SID)
        self.assertEqual(
            message.twilio_message_sid, "XXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )
        self.assertEqual(message.dt, mock_now.return_value)
