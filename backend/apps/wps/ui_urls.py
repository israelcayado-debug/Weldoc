from django.urls import path

from . import ui


urlpatterns = [
    path("", ui.wps_list, name="wps_list"),
    path("new/", ui.wps_create, name="wps_create"),
    path("<uuid:pk>/", ui.wps_detail, name="wps_detail"),
    path("<uuid:pk>/edit/", ui.wps_edit, name="wps_edit"),
    path("<uuid:pk>/qw482/", ui.wps_qw482_form, name="wps_qw482_form"),
    path("<uuid:pk>/processes/", ui.wps_process_list, name="wps_process_list"),
    path("<uuid:pk>/processes/new/", ui.wps_process_create, name="wps_process_create"),
    path("processes/<uuid:process_id>/edit/", ui.wps_process_edit, name="wps_process_edit"),
    path("processes/<uuid:process_id>/variables/", ui.wps_process_variables, name="wps_process_variables"),
]
