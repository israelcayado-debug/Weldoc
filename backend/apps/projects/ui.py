from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import ClientForm, ProjectForm, ProjectEquipmentForm
from apps.documents import models as document_models
from apps.quality import models as quality_models
from apps.welds import models as weld_models
from apps.wps import models as wps_models
from apps.wpq import models as wpq_models


def _project_copy_code(base_code):
    for index in range(1, 1000):
        suffix = "-COPY" if index == 1 else f"-COPY-{index}"
        trimmed_base = base_code[: max(1, 100 - len(suffix))]
        candidate = f"{trimmed_base}{suffix}"
        if not models.Project.objects.filter(code=candidate).exists():
            return candidate
    return f"{base_code[:91]}-COPY-999"


@login_required
def project_list(request):
    q = request.GET.get("q")
    status = request.GET.get("status")
    welding_book_filter = (
        Q(document__type__iexact="welding book")
        | Q(document__type__iexact="welding_book")
        | Q(document__type__iexact="weldingbook")
        | Q(document__title__icontains="welding book")
    )
    items = (
        models.Project.objects.select_related("client")
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
    if q:
        items = items.filter(Q(name__icontains=q) | Q(code__icontains=q))
    if status:
        items = items.filter(status=status)
    return render(
        request,
        "projects/list.html",
        {"items": items},
    )


@login_required
def project_detail(request, pk):
    item = get_object_or_404(models.Project, pk=pk)
    welding_book_filter = (
        Q(type__iexact="welding book")
        | Q(type__iexact="welding_book")
        | Q(type__iexact="weldingbook")
        | Q(title__icontains="welding book")
    )
    drawings = weld_models.Drawing.objects.filter(project=item).count()
    weld_maps = weld_models.WeldMap.objects.filter(project=item).count()
    welds = weld_models.Weld.objects.filter(project=item).count()
    welding_books = document_models.Document.objects.filter(project=item).filter(
        welding_book_filter
    ).count()
    wps_count = wps_models.Wps.objects.filter(project=item).count()
    pqr_count = wps_models.Pqr.objects.filter(project=item).count()
    nde_requests = quality_models.NdeRequest.objects.filter(project=item).count()
    pwht_records = quality_models.PwhtRecord.objects.filter(weld__project=item).count()
    pressure_tests = quality_models.PressureTest.objects.filter(project=item).count()
    project_users = (
        models.ProjectUser.objects.select_related("user", "role")
        .filter(project=item)
        .order_by("role__name", "user__name")
    )
    project_equipment = (
        models.ProjectEquipment.objects.filter(project=item).order_by("name")
    )
    assigned_welders = (
        wpq_models.Welder.objects.filter(weldwelderassignment__weld__project=item)
        .distinct()
        .order_by("name")
    )
    welder_qualification = []
    for welder in assigned_welders:
        has_wpq = wpq_models.Wpq.objects.filter(
            welder=welder,
            standard="ASME_IX",
            status="approved",
        ).exists()
        welder_qualification.append({"welder": welder, "has_wpq": has_wpq})
    return render(
        request,
        "projects/detail.html",
        {
            "item": item,
            "drawings": drawings,
            "weld_maps": weld_maps,
            "welds": welds,
            "welding_books": welding_books,
            "wps_count": wps_count,
            "pqr_count": pqr_count,
            "nde_requests": nde_requests,
            "pwht_records": pwht_records,
            "pressure_tests": pressure_tests,
            "project_users": project_users,
            "project_equipment": project_equipment,
            "welder_qualification": welder_qualification,
        },
    )


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, require_equipment=True)
        if form.is_valid():
            item = form.save()
            models.ProjectEquipment.objects.create(
                project=item,
                name=form.cleaned_data["equipment_name"].strip(),
                fabrication_code=form.cleaned_data["equipment_fabrication_code"].strip(),
                status="active",
            )
            return redirect("project_detail", pk=item.pk)
    else:
        form = ProjectForm(require_equipment=True)
    return render(request, "projects/form.html", {"form": form, "title": "New project"})


@login_required
def project_edit(request, pk):
    item = get_object_or_404(models.Project, pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("project_detail", pk=item.pk)
    else:
        form = ProjectForm(instance=item)
    return render(request, "projects/form.html", {"form": form, "title": "Edit project"})


@login_required
def project_copy(request, pk):
    if request.method != "POST":
        return redirect("project_list")

    source = get_object_or_404(models.Project, pk=pk)
    copy_code = _project_copy_code(source.code)

    with transaction.atomic():
        project_copy = models.Project.objects.create(
            client=source.client,
            name=f"{source.name} (Copy)",
            code=copy_code,
            purchase_order=source.purchase_order,
            units=source.units,
            status=source.status,
            standard_set=source.standard_set,
        )
        source_equipment = models.ProjectEquipment.objects.filter(project=source)
        models.ProjectEquipment.objects.bulk_create(
            [
                models.ProjectEquipment(
                    project=project_copy,
                    name=item.name,
                    fabrication_code=item.fabrication_code,
                    status=item.status,
                )
                for item in source_equipment
            ]
        )

    return redirect("project_detail", pk=project_copy.pk)


@login_required
def project_delete(request, pk):
    if request.method == "POST":
        item = get_object_or_404(models.Project, pk=pk)
        item.delete()
    return redirect("project_list")


@login_required
def project_equipment_list(request, project_id):
    project = get_object_or_404(models.Project, pk=project_id)
    items = models.ProjectEquipment.objects.filter(project=project).order_by("name")
    return render(
        request,
        "projects/equipment_list.html",
        {"project": project, "items": items},
    )


@login_required
def project_equipment_create(request, project_id):
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = ProjectEquipmentForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.project = project
            item.save()
            return redirect("project_equipment_list", project_id=project.id)
    else:
        form = ProjectEquipmentForm(initial={"project": project, "status": "active"})
    form.fields["project"].widget = forms.HiddenInput()
    return render(
        request,
        "projects/equipment_form.html",
        {"form": form, "title": "New equipment", "project": project},
    )


@login_required
def project_equipment_edit(request, pk):
    item = get_object_or_404(models.ProjectEquipment, pk=pk)
    project = item.project
    if request.method == "POST":
        form = ProjectEquipmentForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("project_equipment_list", project_id=project.id)
    else:
        form = ProjectEquipmentForm(instance=item)
    form.fields["project"].widget = forms.HiddenInput()
    return render(
        request,
        "projects/equipment_form.html",
        {"form": form, "title": "Edit equipment", "project": project},
    )


@login_required
def client_list(request):
    q = request.GET.get("q")
    status = request.GET.get("status")
    items = models.Client.objects.all().order_by("name")
    if q:
        items = items.filter(name__icontains=q)
    if status:
        items = items.filter(status=status)
    return render(request, "projects/clients_list.html", {"items": items})


@login_required
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm()
    return render(request, "projects/clients_form.html", {"form": form, "title": "New customer"})


@login_required
def client_edit(request, pk):
    item = get_object_or_404(models.Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm(instance=item)
    return render(request, "projects/clients_form.html", {"form": form, "title": "Edit customer"})
