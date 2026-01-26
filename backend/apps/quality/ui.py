import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import NdeRequestForm, NdeResultForm, PwhtRecordForm, PressureTestForm


@login_required
def nde_request_list(request):
    project_id = request.GET.get("project_id")
    status = request.GET.get("status")
    items = models.NdeRequest.objects.select_related("project", "weld").all().order_by("-requested_at")
    if project_id:
        items = items.filter(project_id=project_id)
    if status:
        items = items.filter(status=status)
    return render(request, "quality/nde_requests/list.html", {"items": items})


@login_required
def nde_request_detail(request, pk):
    item = get_object_or_404(models.NdeRequest, pk=pk)
    results = models.NdeResult.objects.filter(nde_request=item).order_by("id")
    return render(request, "quality/nde_requests/detail.html", {"item": item, "results": results})


@login_required
def nde_request_create(request):
    if request.method == "POST":
        form = NdeRequestForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("nde_request_detail", pk=item.pk)
    else:
        form = NdeRequestForm()
    return render(request, "quality/nde_requests/form.html", {"form": form, "title": "Nuevo END"})


@login_required
def nde_request_edit(request, pk):
    item = get_object_or_404(models.NdeRequest, pk=pk)
    if request.method == "POST":
        form = NdeRequestForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("nde_request_detail", pk=item.pk)
    else:
        form = NdeRequestForm(instance=item)
    return render(request, "quality/nde_requests/form.html", {"form": form, "title": "Editar END"})


@login_required
def nde_result_create(request, pk):
    nde_request = get_object_or_404(models.NdeRequest, pk=pk)
    if request.method == "POST":
        form = NdeResultForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.nde_request = nde_request
            upload = form.cleaned_data.get("upload")
            if upload:
                filename = f"{uuid.uuid4().hex}_{upload.name}"
                rel_path = os.path.join("quality", "nde", filename)
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "wb") as handle:
                    for chunk in upload.chunks():
                        handle.write(chunk)
                item.report_path = rel_path
            else:
                item.report_path = ""
            item.save()
            return redirect("nde_request_detail", pk=nde_request.pk)
    else:
        form = NdeResultForm(initial={"nde_request": nde_request.id})
    return render(
        request,
        "quality/nde_requests/result_form.html",
        {"form": form, "title": "Nuevo resultado", "nde_request": nde_request},
    )


@login_required
def pwht_list(request):
    weld_id = request.GET.get("weld_id")
    items = models.PwhtRecord.objects.select_related("weld").all().order_by("-id")
    if weld_id:
        items = items.filter(weld_id=weld_id)
    return render(request, "quality/pwht/list.html", {"items": items})


@login_required
def pwht_detail(request, pk):
    item = get_object_or_404(models.PwhtRecord, pk=pk)
    return render(request, "quality/pwht/detail.html", {"item": item})


@login_required
def pwht_create(request):
    if request.method == "POST":
        form = PwhtRecordForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            upload = form.cleaned_data.get("upload")
            if upload:
                filename = f"{uuid.uuid4().hex}_{upload.name}"
                rel_path = os.path.join("quality", "pwht", filename)
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "wb") as handle:
                    for chunk in upload.chunks():
                        handle.write(chunk)
                item.report_path = rel_path
            else:
                item.report_path = ""
            item.save()
            return redirect("pwht_detail", pk=item.pk)
    else:
        form = PwhtRecordForm()
    return render(request, "quality/pwht/form.html", {"form": form, "title": "Nuevo PWHT"})


@login_required
def pwht_edit(request, pk):
    item = get_object_or_404(models.PwhtRecord, pk=pk)
    if request.method == "POST":
        form = PwhtRecordForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            upload = form.cleaned_data.get("upload")
            if upload:
                filename = f"{uuid.uuid4().hex}_{upload.name}"
                rel_path = os.path.join("quality", "pwht", filename)
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "wb") as handle:
                    for chunk in upload.chunks():
                        handle.write(chunk)
                item.report_path = rel_path
            item.save()
            return redirect("pwht_detail", pk=item.pk)
    else:
        form = PwhtRecordForm(instance=item)
    return render(request, "quality/pwht/form.html", {"form": form, "title": "Editar PWHT"})


@login_required
def pressure_test_list(request):
    project_id = request.GET.get("project_id")
    items = models.PressureTest.objects.select_related("project").all().order_by("-id")
    if project_id:
        items = items.filter(project_id=project_id)
    return render(request, "quality/pressure_tests/list.html", {"items": items})


@login_required
def pressure_test_detail(request, pk):
    item = get_object_or_404(models.PressureTest, pk=pk)
    return render(request, "quality/pressure_tests/detail.html", {"item": item})


@login_required
def pressure_test_create(request):
    if request.method == "POST":
        form = PressureTestForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            upload = form.cleaned_data.get("upload")
            if upload:
                filename = f"{uuid.uuid4().hex}_{upload.name}"
                rel_path = os.path.join("quality", "pressure", filename)
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "wb") as handle:
                    for chunk in upload.chunks():
                        handle.write(chunk)
                item.report_path = rel_path
            else:
                item.report_path = ""
            item.save()
            return redirect("pressure_test_detail", pk=item.pk)
    else:
        form = PressureTestForm()
    return render(request, "quality/pressure_tests/form.html", {"form": form, "title": "Nueva prueba de presion"})


@login_required
def pressure_test_edit(request, pk):
    item = get_object_or_404(models.PressureTest, pk=pk)
    if request.method == "POST":
        form = PressureTestForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            upload = form.cleaned_data.get("upload")
            if upload:
                filename = f"{uuid.uuid4().hex}_{upload.name}"
                rel_path = os.path.join("quality", "pressure", filename)
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "wb") as handle:
                    for chunk in upload.chunks():
                        handle.write(chunk)
                item.report_path = rel_path
            item.save()
            return redirect("pressure_test_detail", pk=item.pk)
    else:
        form = PressureTestForm(instance=item)
    return render(request, "quality/pressure_tests/form.html", {"form": form, "title": "Editar prueba de presion"})
