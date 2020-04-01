from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("case/<int:case_pk>", views.case_details, name="case_details"),
    path("create/<int:case_id>", views.create, name="create"),
]
