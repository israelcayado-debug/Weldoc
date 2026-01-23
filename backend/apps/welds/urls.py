from django.urls import path
from . import views


urlpatterns = [
    path("welds/", views.WeldViewSet.as_view({"get": "list"})),
    path("welds/<uuid:pk>/", views.WeldViewSet.as_view({"get": "retrieve"})),
]
