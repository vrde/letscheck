from django.contrib import admin

from .models import News, Rating, Case

admin.site.register(News)
admin.site.register(Rating)
admin.site.register(Case)
