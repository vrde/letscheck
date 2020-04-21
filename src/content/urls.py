from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.index, name="content_index"),
    path("how-it-works", views.how_it_works, name="content_how_it_works"),
]
