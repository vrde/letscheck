from unittest.mock import patch, call

from django.test import RequestFactory, TestCase
from django.http import HttpResponseBadRequest, Http404


class InboxWhatsappTest(TestCase):
    def setUp(self):
        self.request = RequestFactory()

    def test_should_return_404_on_get(self):
        from .views import inbox_whatsapp
        from .models import Message, Media

        request = self.request.get("chat/inbox/whatsapp")
        with self.assertRaises(Http404):
            inbox_whatsapp(request)

    @patch("chat.views.async_task")
    def test_should_process_simple_message(self, mock_task):
        from .views import inbox_whatsapp
        from .models import Message, Media

        request = self.request.post(
            "chat/inbox/whatsapp",
            {
                "AccountSid": "AC7e46427afac98c1862924007620275ca",
                "ApiVersion": "2010-04-01",
                "Body": "Hello, World!",
                "From": "whatsapp:+4911111111111",
                "MessageSid": "SMd31271180bcddbeb25a57407bae162fb",
                "NumMedia": "0",
                "NumSegments": "1",
                "SmsMessageSid": "SMd31271180bcddbeb25a57407bae162fb",
                "SmsSid": "SMd31271180bcddbeb25a57407bae162fb",
                "SmsStatus": "received",
                "To": "whatsapp:+11111111111",
            },
        )
        response = inbox_whatsapp(request)
        self.assertEqual(response.status_code, 200)
        messages = Message.objects.filter(sender__exact="+4911111111111")
        self.assertEqual(messages.count(), 1)
        message = messages.first()
        self.assertEqual(message.carrier, "whatsapp")
        self.assertEqual(message.sender, "+4911111111111")
        self.assertEqual(message.receiver, "+11111111111")
        self.assertEqual(message.media_set.count(), 0)
        mock_task.assert_not_called()

    @patch("chat.views.async_task")
    def test_should_process_message_with_media_without_body(self, mock_task):
        from .views import inbox_whatsapp
        from .models import Message, Media

        request = self.request.post(
            "chat/inbox/whatsapp",
            {
                "AccountSid": "AC7e46427afac98c1862924007620275ca",
                "ApiVersion": "2010-04-01",
                "From": "whatsapp:+4911111111111",
                "MessageSid": "SMd31271180bcddbeb25a57407bae162fb",
                "NumMedia": "2",
                "NumSegments": "1",
                "MediaContentType0": "application/pdf",
                "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/0",
                "MediaContentType1": "image/png",
                "MediaUrl1": "https://api.twilio.com/2010-04-01/Accounts/1",
                "SmsMessageSid": "SMd31271180bcddbeb25a57407bae162fb",
                "SmsSid": "SMd31271180bcddbeb25a57407bae162fb",
                "SmsStatus": "received",
                "To": "whatsapp:+11111111111",
            },
        )
        response = inbox_whatsapp(request)
        self.assertEqual(response.status_code, 200)
        messages = Message.objects.filter(sender__exact="+4911111111111")
        self.assertEqual(messages.count(), 1)
        message = messages.first()
        self.assertEqual(message.carrier, "whatsapp")
        self.assertEqual(message.sender, "+4911111111111")
        self.assertEqual(message.receiver, "+11111111111")
        self.assertEqual(message.media_set.count(), 2)
        media = message.media_set.all()
        self.assertEqual(media[0].content_type, "application/pdf")
        self.assertEqual(media[0].url, "https://api.twilio.com/2010-04-01/Accounts/0")
        self.assertEqual(media[1].content_type, "image/png")
        self.assertEqual(media[1].url, "https://api.twilio.com/2010-04-01/Accounts/1")
        mock_task.assert_has_calls(
            [
                call().async_task("chat.tasks.download_media", media[0].pk),
                call().async_task("chat.tasks.download_media", media[1].pk),
            ]
        )

    @patch("chat.views.async_task")
    def test_should_process_message_with_media(self, mock_task):
        from .views import inbox_whatsapp
        from .models import Message, Media

        request = self.request.post(
            "chat/inbox/whatsapp",
            {
                "AccountSid": "AC7e46427afac98c1862924007620275ca",
                "ApiVersion": "2010-04-01",
                "Body": "Hello, World!",
                "From": "whatsapp:+4911111111111",
                "MessageSid": "SMd31271180bcddbeb25a57407bae162fb",
                "NumMedia": "2",
                "NumSegments": "1",
                "MediaContentType0": "application/pdf",
                "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/0",
                "MediaContentType1": "image/png",
                "MediaUrl1": "https://api.twilio.com/2010-04-01/Accounts/1",
                "SmsMessageSid": "SMd31271180bcddbeb25a57407bae162fb",
                "SmsSid": "SMd31271180bcddbeb25a57407bae162fb",
                "SmsStatus": "received",
                "To": "whatsapp:+11111111111",
            },
        )
        response = inbox_whatsapp(request)
        self.assertEqual(response.status_code, 200)
        messages = Message.objects.filter(sender__exact="+4911111111111")
        self.assertEqual(messages.count(), 1)
        message = messages.first()
        self.assertEqual(message.carrier, "whatsapp")
        self.assertEqual(message.sender, "+4911111111111")
        self.assertEqual(message.receiver, "+11111111111")
        self.assertEqual(message.media_set.count(), 2)
        media = message.media_set.all()
        self.assertEqual(media[0].content_type, "application/pdf")
        self.assertEqual(media[0].url, "https://api.twilio.com/2010-04-01/Accounts/0")
        self.assertEqual(media[1].content_type, "image/png")
        self.assertEqual(media[1].url, "https://api.twilio.com/2010-04-01/Accounts/1")
        mock_task.assert_has_calls(
            [
                call().async_task("chat.tasks.download_media", media[0].pk),
                call().async_task("chat.tasks.download_media", media[1].pk),
            ]
        )

    @patch("django_q.tasks.async_task")
    def test_should_reject_messages_with_wrong_number_of_media(self, mock_task):
        from .views import inbox_whatsapp
        from .models import Message, Media

        request = self.request.post(
            "chat/inbox/whatsapp",
            {
                "AccountSid": "AC7e46427afac98c1862924007620275ca",
                "ApiVersion": "2010-04-01",
                "Body": "Hello, World!",
                "From": "whatsapp:+4911111111111",
                "MessageSid": "SMd31271180bcddbeb25a57407bae162fb",
                "NumMedia": "2",
                "NumSegments": "1",
                "MediaContentType0": "application/pdf",
                "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/0",
                "SmsMessageSid": "SMd31271180bcddbeb25a57407bae162fb",
                "SmsSid": "SMd31271180bcddbeb25a57407bae162fb",
                "SmsStatus": "received",
                "To": "whatsapp:+11111111111",
            },
        )
        response = inbox_whatsapp(request)
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

    @patch("tempfile.NamedTemporaryFile")
    @patch("requests.get", return_value=MockResponse(MOCK_CHUNKS))
    @patch("shutil.move")
    def test_should_download_the_file_calculate_sha_and_store(
        self, mock_move, mock_response, mock_temp_file
    ):
        from hashlib import sha256
        from .views import inbox_whatsapp
        from .models import Message, Media
        from .tasks import download_media

        mock_temp_file.name.return_value = "tempname"

        h = sha256()
        h.update(b"".join(self.MOCK_CHUNKS))

        message = Message.objects.create(
            carrier="test", sender="test", receiver="test", body="test"
        )
        media = message.media_set.create(
            url="http://example.com/media.txt", content_type="text"
        )
        message.save()
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
