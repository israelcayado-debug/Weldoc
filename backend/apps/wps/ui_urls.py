from django.urls import path

from . import ui


urlpatterns = [
    path("", ui.wps_list, name="wps_list"),
    path("new/", ui.wps_create, name="wps_create"),
    path("<uuid:pk>/", ui.wps_detail, name="wps_detail"),
    path("<uuid:pk>/edit/", ui.wps_edit, name="wps_edit"),
]
