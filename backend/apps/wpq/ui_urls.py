from django.urls import path

from . import ui


urlpatterns = [
    path("", ui.wpq_list, name="wpq_list"),
    path("new/", ui.wpq_create, name="wpq_create"),
    path("<uuid:pk>/", ui.wpq_detail, name="wpq_detail"),
    path("<uuid:pk>/edit/", ui.wpq_edit, name="wpq_edit"),
]
