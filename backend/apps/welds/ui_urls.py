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
    path("drawings/<uuid:pk>/new-revision/", ui.drawing_new_revision, name="drawing_new_revision"),
    path("drawings/<uuid:pk>/copy-marks/", ui.drawing_copy_marks, name="drawing_copy_marks"),
    path("weld-maps/", ui.weld_map_list, name="weld_map_list"),
    path("weld-maps/new/", ui.weld_map_create, name="weld_map_create"),
    path("weld-maps/<uuid:pk>/", ui.weld_map_detail, name="weld_map_detail"),
    path("weld-maps/<uuid:pk>/edit/", ui.weld_map_edit, name="weld_map_edit"),
    path("weld-attributes/", ui.weld_attribute_list, name="weld_attribute_list"),
    path("weld-attributes/new/", ui.weld_attribute_create, name="weld_attribute_create"),
    path("weld-attributes/<uuid:pk>/", ui.weld_attribute_detail, name="weld_attribute_detail"),
    path("weld-attributes/<uuid:pk>/edit/", ui.weld_attribute_edit, name="weld_attribute_edit"),
    path("weld-materials/", ui.weld_material_list, name="weld_material_list"),
    path("weld-materials/new/", ui.weld_material_create, name="weld_material_create"),
    path("weld-materials/<uuid:pk>/", ui.weld_material_detail, name="weld_material_detail"),
    path("weld-materials/<uuid:pk>/edit/", ui.weld_material_edit, name="weld_material_edit"),
    path("weld-consumables/", ui.weld_consumable_list, name="weld_consumable_list"),
    path("weld-consumables/new/", ui.weld_consumable_create, name="weld_consumable_create"),
    path("weld-consumables/<uuid:pk>/", ui.weld_consumable_detail, name="weld_consumable_detail"),
    path("weld-consumables/<uuid:pk>/edit/", ui.weld_consumable_edit, name="weld_consumable_edit"),
    path("visual-inspections/", ui.visual_inspection_list, name="visual_inspection_list"),
    path("visual-inspections/new/", ui.visual_inspection_create, name="visual_inspection_create"),
    path("visual-inspections/<uuid:pk>/", ui.visual_inspection_detail, name="visual_inspection_detail"),
    path("visual-inspections/<uuid:pk>/edit/", ui.visual_inspection_edit, name="visual_inspection_edit"),
]
