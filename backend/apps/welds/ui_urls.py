from django.urls import path

from . import ui


urlpatterns = [
    path("", ui.weld_list, name="weld_list"),
    path("new/", ui.weld_create, name="weld_create"),
    path("<uuid:pk>/", ui.weld_detail, name="weld_detail"),
    path("<uuid:pk>/edit/", ui.weld_edit, name="weld_edit"),
    path("drawings/", ui.drawing_list, name="drawing_list"),
    path("drawings/new/", ui.drawing_create, name="drawing_create"),
    path("drawings/<uuid:pk>/", ui.drawing_detail, name="drawing_detail"),
    path("drawings/<uuid:pk>/edit/", ui.drawing_edit, name="drawing_edit"),
    path("weld-maps/", ui.weld_map_list, name="weld_map_list"),
    path("weld-maps/new/", ui.weld_map_create, name="weld_map_create"),
    path("weld-maps/<uuid:pk>/", ui.weld_map_detail, name="weld_map_detail"),
    path("weld-maps/<uuid:pk>/edit/", ui.weld_map_edit, name="weld_map_edit"),
]
