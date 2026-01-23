import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import DrawingForm, WeldForm, WeldMapForm


@login_required
def weld_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    items = models.Weld.objects.select_related("project").all().order_by("number")
    if q:
        items = items.filter(number__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
    return render(request, "welds/list.html", {"items": items})


@login_required
def weld_detail(request, pk):
    item = get_object_or_404(models.Weld, pk=pk)
    return render(request, "welds/detail.html", {"item": item})


@login_required
def weld_create(request):
    if request.method == "POST":
        form = WeldForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("weld_detail", pk=item.pk)
    else:
        form = WeldForm()
    return render(request, "welds/form.html", {"form": form, "title": "Nueva soldadura"})


@login_required
def weld_edit(request, pk):
    item = get_object_or_404(models.Weld, pk=pk)
    if request.method == "POST":
        form = WeldForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("weld_detail", pk=item.pk)
    else:
        form = WeldForm(instance=item)
    return render(request, "welds/form.html", {"form": form, "title": "Editar soldadura"})


@login_required
def drawing_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    items = models.Drawing.objects.select_related("project").all().order_by("code")
    if q:
        items = items.filter(Q(code__icontains=q) | Q(revision__icontains=q))
    if project_id:
        items = items.filter(project_id=project_id)
    return render(request, "drawings/list.html", {"items": items})


@login_required
def drawing_detail(request, pk):
    item = get_object_or_404(models.Drawing, pk=pk)
    return render(request, "drawings/detail.html", {"item": item})


@login_required
def drawing_create(request):
    if request.method == "POST":
        form = DrawingForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            upload = form.cleaned_data.get("upload")
            if upload:
                filename = f"{uuid.uuid4().hex}_{upload.name}"
                rel_path = os.path.join("drawings", filename)
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "wb") as handle:
                    for chunk in upload.chunks():
                        handle.write(chunk)
                item.file_path = rel_path
            else:
                item.file_path = ""
            item.save()
            return redirect("drawing_detail", pk=item.pk)
    else:
        form = DrawingForm()
    return render(request, "drawings/form.html", {"form": form, "title": "Nuevo plano"})


@login_required
def drawing_edit(request, pk):
    item = get_object_or_404(models.Drawing, pk=pk)
    if request.method == "POST":
        form = DrawingForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            upload = form.cleaned_data.get("upload")
            if upload:
                filename = f"{uuid.uuid4().hex}_{upload.name}"
                rel_path = os.path.join("drawings", filename)
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, "wb") as handle:
                    for chunk in upload.chunks():
                        handle.write(chunk)
                item.file_path = rel_path
            else:
                item.file_path = ""
            item.save()
            return redirect("drawing_detail", pk=item.pk)
    else:
        form = DrawingForm(instance=item)
    return render(request, "drawings/form.html", {"form": form, "title": "Editar plano"})


@login_required
def weld_map_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    drawing_id = request.GET.get("drawing_id")
    items = models.WeldMap.objects.select_related("project", "drawing").all().order_by("drawing__code")
    if q:
        items = items.filter(drawing__code__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
    if drawing_id:
        items = items.filter(drawing_id=drawing_id)
    return render(request, "weld_maps/list.html", {"items": items})


@login_required
def weld_map_detail(request, pk):
    item = get_object_or_404(models.WeldMap, pk=pk)
    return render(request, "weld_maps/detail.html", {"item": item})


@login_required
def weld_map_create(request):
    if request.method == "POST":
        form = WeldMapForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("weld_map_detail", pk=item.pk)
    else:
        form = WeldMapForm()
    return render(request, "weld_maps/form.html", {"form": form, "title": "Nuevo welding map"})


@login_required
def weld_map_edit(request, pk):
    item = get_object_or_404(models.WeldMap, pk=pk)
    if request.method == "POST":
        form = WeldMapForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("weld_map_detail", pk=item.pk)
    else:
        form = WeldMapForm(instance=item)
    return render(request, "weld_maps/form.html", {"form": form, "title": "Editar welding map"})
