from django.urls import include, path
from . import views

urlpatterns = [path("inbox/whatsapp", views.inbox_whatsapp, name="inbox_whatsapp")]
