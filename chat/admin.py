from django.contrib import admin

from .models import Message, Media

admin.site.register(Message)
admin.site.register(Media)
