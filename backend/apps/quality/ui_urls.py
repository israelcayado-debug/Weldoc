from django.urls import path

from . import ui


urlpatterns = [
    path("nde-requests/", ui.nde_request_list, name="nde_request_list"),
    path("nde-requests/new/", ui.nde_request_create, name="nde_request_create"),
    path("nde-requests/<uuid:pk>/", ui.nde_request_detail, name="nde_request_detail"),
    path("nde-requests/<uuid:pk>/edit/", ui.nde_request_edit, name="nde_request_edit"),
    path("nde-requests/<uuid:pk>/results/new/", ui.nde_result_create, name="nde_result_create"),
    path("pwht/", ui.pwht_list, name="pwht_list"),
    path("pwht/new/", ui.pwht_create, name="pwht_create"),
    path("pwht/<uuid:pk>/", ui.pwht_detail, name="pwht_detail"),
    path("pwht/<uuid:pk>/edit/", ui.pwht_edit, name="pwht_edit"),
    path("pressure-tests/", ui.pressure_test_list, name="pressure_test_list"),
    path("pressure-tests/new/", ui.pressure_test_create, name="pressure_test_create"),
    path("pressure-tests/<uuid:pk>/", ui.pressure_test_detail, name="pressure_test_detail"),
    path("pressure-tests/<uuid:pk>/edit/", ui.pressure_test_edit, name="pressure_test_edit"),
]
