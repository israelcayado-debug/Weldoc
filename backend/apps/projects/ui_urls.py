from django.urls import path

from . import ui


urlpatterns = [
    path("", ui.project_list, name="project_list"),
    path("new/", ui.project_create, name="project_create"),
    path("<uuid:pk>/", ui.project_detail, name="project_detail"),
    path("<uuid:pk>/edit/", ui.project_edit, name="project_edit"),
    path("<uuid:pk>/copy/", ui.project_copy, name="project_copy"),
    path("<uuid:pk>/delete/", ui.project_delete, name="project_delete"),
    path("<uuid:project_id>/equipment/", ui.project_equipment_list, name="project_equipment_list"),
    path("<uuid:project_id>/equipment/new/", ui.project_equipment_create, name="project_equipment_create"),
    path("equipment/<uuid:pk>/edit/", ui.project_equipment_edit, name="project_equipment_edit"),
    path("clients/", ui.client_list, name="client_list"),
    path("clients/new/", ui.client_create, name="client_create"),
    path("clients/<uuid:pk>/edit/", ui.client_edit, name="client_edit"),
]
