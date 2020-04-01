from django import forms
from django.utils.timezone import now

from .models import Message, Media


CARRIERS = ["whatsapp"]


class WhatsappMessage(forms.Form):
    From = forms.CharField(max_length=100)
    To = forms.CharField(max_length=100)
    Body = forms.CharField(required=False)
    NumMedia = forms.IntegerField(min_value=0, max_value=50)
    AccountSid = forms.CharField(max_length=34)
    MessageSid = forms.CharField(max_length=34)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(args) > 0:
            query_dict = args[0]
            try:
                num_media = int(query_dict.get("NumMedia", 0))
            except ValueError:
                num_media = 0
            for num in range(num_media):
                self.fields["MediaContentType{}".format(num)] = forms.CharField(
                    max_length=100
                )
                self.fields["MediaUrl{}".format(num)] = forms.CharField(max_length=1024)

    def clean(self):
        cleaned_data = super().clean()
        carrier_sender, _, sender = cleaned_data["From"].partition(":")
        carrier_receiver, _, receiver = cleaned_data["To"].partition(":")
        num_media = cleaned_data["NumMedia"]

        if carrier_sender not in CARRIERS:
            self.add_error("From", "Unknown carrier")

        if carrier_receiver not in CARRIERS:
            self.add_error("To", "Unknown carrier")

        if carrier_sender != carrier_receiver:
            self.add_error("From", "Carriers do not match")
            self.add_error("To", "Carriers do not match")

        cleaned_data["carrier"] = carrier_sender
        cleaned_data["sender"] = sender
        cleaned_data["receiver"] = receiver
        # FIXME: Learn how to properly validate
        cleaned_data["body"] = cleaned_data.get("Body")
        cleaned_data["media"] = []
        cleaned_data["twilio_account_sid"] = cleaned_data["AccountSid"]
        cleaned_data["twilio_message_sid"] = cleaned_data["MessageSid"]

        # FIXME: why do I have to manually check if the fields are defined?
        # They are dynamically added in __init__, that should be enough
        # :thinking_face:
        for num in range(num_media):
            content_type_key = "MediaContentType{}".format(num)
            url_key = "MediaUrl{}".format(num)
            try:
                content_type = cleaned_data[content_type_key]
            except KeyError:
                self.add_error(content_type_key, "Required")
            try:
                url = cleaned_data[url_key]
            except KeyError:
                self.add_error(url_key, "Required")
            cleaned_data["media"].append(
                {"content_type": content_type, "twilio_media_url": url}
            )

    def save(self, commit=True):
        message = Message.objects.create(
            carrier=self.cleaned_data["carrier"],
            sender=self.cleaned_data["sender"],
            receiver=self.cleaned_data["receiver"],
            is_incoming=True,
            body=self.cleaned_data["body"],
            dt=now(),
            twilio_account_sid=self.cleaned_data["twilio_account_sid"],
            twilio_message_sid=self.cleaned_data["twilio_message_sid"],
        )
        for media in self.cleaned_data["media"]:
            message.media_set.create(
                twilio_media_url=media["twilio_media_url"],
                content_type=media["content_type"],
            )
        if commit:
            message.save()
        return message
