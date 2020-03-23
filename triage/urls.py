from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("message/<int:message_id>", views.message, name="message"),
    path("create/<int:message_id>", views.create, name="create"),
]
