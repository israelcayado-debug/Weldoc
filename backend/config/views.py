from django.db.models import Count, Q
from django.shortcuts import render

from apps.projects import models as project_models


def home(request):
    welding_book_filter = (
        Q(document__type__iexact="welding book")
        | Q(document__type__iexact="welding_book")
        | Q(document__type__iexact="weldingbook")
        | Q(document__title__icontains="welding book")
    )
    projects = (
        project_models.Project.objects.all()
        .annotate(
            welding_book_count=Count(
                "document",
                filter=welding_book_filter,
                distinct=True,
            ),
            wps_count=Count("wps", distinct=True),
            pqr_count=Count("pqr", distinct=True),
            welder_count=Count("weld__weldwelderassignment__welder", distinct=True),
        )
        .order_by("code")
    )
    return render(request, "home.html", {"projects": projects})
