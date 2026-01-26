from django.urls import path

from . import ui


urlpatterns = [
    path("exports/", ui.exports, name="report_exports"),
    path("exports/<uuid:export_id>/", ui.export_detail, name="report_export_detail"),
    path("history/", ui.export_history, name="report_export_history"),
]
