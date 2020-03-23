from django.contrib import admin

from .models import News, Rating, MessageToNews

admin.site.register(News)
admin.site.register(Rating)
admin.site.register(MessageToNews)
