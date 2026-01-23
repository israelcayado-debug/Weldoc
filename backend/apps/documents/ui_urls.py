from django.urls import path

from . import ui


urlpatterns = [
    path("", ui.document_list, name="document_list"),
    path("new/", ui.document_create, name="document_create"),
    path("<uuid:pk>/", ui.document_detail, name="document_detail"),
    path("<uuid:pk>/edit/", ui.document_edit, name="document_edit"),
]
