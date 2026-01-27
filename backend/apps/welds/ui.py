import os
import re
import uuid

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import (
    DrawingForm,
    VisualInspectionForm,
    WeldAttributeForm,
    WeldConsumableForm,
    WeldForm,
    WeldMapForm,
    WeldMarkForm,
    WeldMaterialForm,
)


DEFAULT_WELD_PREFIX = "W-"
DEFAULT_WELD_PAD = 4


def _next_weld_number(project, used_numbers):
    existing = models.Weld.objects.filter(
        project=project, number__startswith=DEFAULT_WELD_PREFIX
    ).values_list("number", flat=True)
    max_num = 0
    for number in existing:
        match = re.match(rf"^{re.escape(DEFAULT_WELD_PREFIX)}(\d+)$", number)
        if match:
            max_num = max(max_num, int(match.group(1)))
    used = set(used_numbers)
    counter = max_num + 1

    def generate():
        nonlocal counter
        while True:
            candidate = f"{DEFAULT_WELD_PREFIX}{counter:0{DEFAULT_WELD_PAD}d}"
            counter += 1
            if candidate not in used:
                used.add(candidate)
                return candidate

    return generate


def _inspection_status(item):
    if item.inspection_fail_count:
        return "fail"
    if item.inspection_rework_count:
        return "rework"
    if item.inspection_count:
        return "pass"
    return "none"


def _apply_inspection_filter(items, status_filter):
    if status_filter == "fail":
        return items.filter(visualinspection__result="fail")
    if status_filter == "rework":
        return items.filter(visualinspection__result="rework")
    if status_filter == "pass":
        return items.filter(visualinspection__result="pass").exclude(
            visualinspection__result__in=["fail", "rework"]
        )
    if status_filter == "none":
        return items.filter(visualinspection__isnull=True)
    return items


def _suggest_next_revision(revision):
    if not revision:
        return "A"
    value = str(revision).strip()
    if len(value) == 1 and value.isalpha():
        letter = value.upper()
        if letter == "Z":
            return "AA"
        return chr(ord(letter) + 1)
    if value.isdigit():
        return str(int(value) + 1)
    return ""


@login_required
def weld_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    status_filter = request.GET.get("status")
    drawing_id = request.GET.get("drawing_id")
    inspection_status = request.GET.get("inspection_status")
    inspection_count_expr = Count("visualinspection", distinct=True)
    if inspection_status == "fail":
        inspection_count_expr = Count(
            "visualinspection",
            filter=Q(visualinspection__result="fail"),
            distinct=True,
        )
    elif inspection_status == "rework":
        inspection_count_expr = Count(
            "visualinspection",
            filter=Q(visualinspection__result="rework"),
            distinct=True,
        )
    elif inspection_status == "pass":
        inspection_count_expr = Count(
            "visualinspection",
            filter=Q(visualinspection__result="pass"),
            distinct=True,
        )
    items = (
        models.Weld.objects.select_related("project", "drawing")
        .annotate(
            attribute_count=Count("weldattribute"),
            material_count=Count("weldmaterial"),
            consumable_count=Count("weldconsumable"),
            inspection_count=inspection_count_expr,
            inspection_fail_count=Count(
                "visualinspection", filter=Q(visualinspection__result="fail"), distinct=True
            ),
            inspection_rework_count=Count(
                "visualinspection", filter=Q(visualinspection__result="rework"), distinct=True
            ),
        )
        .order_by("number")
    )
    if q:
        items = items.filter(number__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
    if status_filter:
        items = items.filter(status=status_filter)
    if drawing_id:
        items = items.filter(drawing_id=drawing_id)
    if inspection_status:
        items = _apply_inspection_filter(items, inspection_status)
    items = list(items)
    for item in items:
        item.inspection_status = _inspection_status(item)
    return render(request, "welds/list.html", {"items": items})


@login_required
def weld_detail(request, pk):
    item = get_object_or_404(models.Weld, pk=pk)
    attributes = models.WeldAttribute.objects.filter(weld=item).order_by("name")
    materials = models.WeldMaterial.objects.filter(weld=item).select_related("material")
    consumables = models.WeldConsumable.objects.filter(weld=item).select_related("consumable")
    inspections = models.VisualInspection.objects.filter(weld=item).order_by("-at")
    return render(
        request,
        "welds/detail.html",
        {
            "item": item,
            "attributes": attributes,
            "materials": materials,
            "consumables": consumables,
            "inspections": inspections,
        },
    )


@login_required
def weld_create(request):
    if request.method == "POST":
        form = WeldForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("weld_detail", pk=item.pk)
    else:
        form = WeldForm()
    return render(request, "welds/form.html", {"form": form, "title": "New weld"})


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
    return render(request, "welds/form.html", {"form": form, "title": "Edit weld"})


@login_required
def drawing_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    equipment_id = request.GET.get("equipment_id")
    items = models.Drawing.objects.select_related("project", "equipment").all().order_by("code")
    if q:
        items = items.filter(Q(code__icontains=q) | Q(revision__icontains=q))
    if project_id:
        items = items.filter(project_id=project_id)
    if equipment_id:
        items = items.filter(equipment_id=equipment_id)
    return render(request, "drawings/list.html", {"items": items})


@login_required
def drawing_detail(request, pk):
    item = get_object_or_404(models.Drawing, pk=pk)
    revisions = models.Drawing.objects.filter(
        project=item.project,
        code=item.code,
    ).order_by("-id")
    return render(
        request,
        "drawings/detail.html",
        {"item": item, "revisions": revisions},
    )


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
    return render(request, "drawings/form.html", {"form": form, "title": "New drawing"})


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
    return render(request, "drawings/form.html", {"form": form, "title": "Edit drawing"})


@login_required
def drawing_new_revision(request, pk):
    source = get_object_or_404(models.Drawing, pk=pk)
    latest = models.Drawing.objects.filter(
        project=source.project,
        code=source.code,
    ).order_by("-id").first()
    suggested = _suggest_next_revision(latest.revision if latest else None)
    project = source.project
    code = source.code
    equipment = source.equipment
    if request.method == "POST":
        form = DrawingForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.project = project
            item.code = code
            if equipment:
                item.equipment = equipment
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
        initial = {
            "project": project,
            "code": code,
            "revision": suggested,
            "status": "active",
        }
        if equipment:
            initial["equipment"] = equipment
        form = DrawingForm(initial=initial)
    form.fields["project"].widget = forms.HiddenInput()
    if equipment:
        form.fields["equipment"].widget = forms.HiddenInput()
    form.fields["code"].widget = forms.HiddenInput()
    return render(
        request,
        "drawings/form.html",
        {"form": form, "title": "New revision", "source": source},
    )


@login_required
def drawing_copy_marks(request, pk):
    target = get_object_or_404(models.Drawing, pk=pk)
    if request.method != "POST":
        return redirect("drawing_detail", pk=target.pk)
    source_id = request.POST.get("source_id")
    if not source_id:
        return redirect("drawing_detail", pk=target.pk)
    source = get_object_or_404(
        models.Drawing,
        pk=source_id,
        project=target.project,
        code=target.code,
    )
    source_map = models.WeldMap.objects.filter(
        project=target.project,
        drawing=source,
    ).first()
    if not source_map:
        return redirect("drawing_detail", pk=target.pk)
    target_map, _ = models.WeldMap.objects.get_or_create(
        project=target.project,
        drawing=target,
        defaults={"status": "active"},
    )
    source_marks = models.WeldMark.objects.filter(
        weld_map=source_map
    ).select_related("weld")
    for mark in source_marks:
        weld_number = mark.weld.number
        weld, created = models.Weld.objects.get_or_create(
            project=target.project,
            number=weld_number,
            defaults={"drawing": target, "status": "planned"},
        )
        if not created and weld.drawing_id != target.id:
            weld.drawing = target
            weld.save(update_fields=["drawing"])
        exists = models.WeldMark.objects.filter(
            weld_map=target_map,
            weld=weld,
            geometry=mark.geometry,
        ).exists()
        if not exists:
            models.WeldMark.objects.create(
                weld_map=target_map,
                weld=weld,
                geometry=mark.geometry,
            )
        source_attrs = models.WeldAttribute.objects.filter(weld=mark.weld)
        for attr in source_attrs:
            models.WeldAttribute.objects.get_or_create(
                weld=weld,
                name=attr.name,
                defaults={"value": attr.value},
            )
        source_materials = models.WeldMaterial.objects.filter(weld=mark.weld)
        for material in source_materials:
            models.WeldMaterial.objects.get_or_create(
                weld=weld,
                material=material.material,
                heat_number=material.heat_number,
            )
        source_consumables = models.WeldConsumable.objects.filter(weld=mark.weld)
        for consumable in source_consumables:
            models.WeldConsumable.objects.get_or_create(
                weld=weld,
                consumable=consumable.consumable,
                batch=consumable.batch,
            )
    return redirect("drawing_detail", pk=target.pk)


@login_required
def weld_map_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    drawing_id = request.GET.get("drawing_id")
    equipment_id = request.GET.get("equipment_id")
    items = models.WeldMap.objects.select_related(
        "project", "drawing", "drawing__equipment"
    ).all().order_by("drawing__code")
    if q:
        items = items.filter(drawing__code__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
    if drawing_id:
        items = items.filter(drawing_id=drawing_id)
    if equipment_id:
        items = items.filter(drawing__equipment_id=equipment_id)
    return render(request, "weld_maps/list.html", {"items": items})


@login_required
def weld_map_detail(request, pk):
    item = get_object_or_404(models.WeldMap, pk=pk)
    marks = models.WeldMark.objects.filter(weld_map=item).select_related("weld").order_by("-created_at")
    form = WeldMarkForm()
    if request.method == "POST":
        form = WeldMarkForm(request.POST)
        if form.is_valid():
            attributes = form.cleaned_data["attributes_json"]
            marks_payload = form.cleaned_data.get("marks_json") or []
            if not marks_payload:
                weld_number = form.cleaned_data.get("weld_number")
                geometry = form.cleaned_data.get("geometry_json")
                if geometry:
                    marks_payload = [{"number": weld_number, "geometry": geometry}]
            existing_numbers = set(
                models.Weld.objects.filter(project=item.project).values_list("number", flat=True)
            )
            used_numbers = {
                mark.get("number")
                for mark in marks_payload
                if isinstance(mark, dict) and mark.get("number")
            }
            next_number = _next_weld_number(item.project, existing_numbers | used_numbers)
            created = 0
            for mark in marks_payload:
                if not isinstance(mark, dict):
                    continue
                weld_number = mark.get("number")
                geometry = mark.get("geometry")
                if not geometry:
                    continue
                if not weld_number:
                    weld_number = next_number()
                weld, _ = models.Weld.objects.get_or_create(
                    project=item.project,
                    number=weld_number,
                    defaults={"drawing": item.drawing, "status": "planned"},
                )
                models.WeldMark.objects.create(weld_map=item, weld=weld, geometry=geometry)
                for attr in attributes:
                    name = attr.get("name") if isinstance(attr, dict) else None
                    value = attr.get("value") if isinstance(attr, dict) else None
                    if name and value is not None:
                        models.WeldAttribute.objects.create(weld=weld, name=name, value=str(value))
                created += 1
            if not created:
                form.add_error(None, "Debe agregar al menos una marca valida.")
                return render(
                    request,
                    "weld_maps/detail.html",
                    {"item": item, "marks": marks, "form": form},
                )
            return redirect("weld_map_detail", pk=item.pk)
    return render(
        request,
        "weld_maps/detail.html",
        {"item": item, "marks": marks, "form": form},
    )


@login_required
def weld_map_create(request):
    if request.method == "POST":
        form = WeldMapForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("weld_map_detail", pk=item.pk)
    else:
        form = WeldMapForm()
    return render(request, "weld_maps/form.html", {"form": form, "title": "New welding map"})


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
    return render(request, "weld_maps/form.html", {"form": form, "title": "Edit welding map"})


@login_required
def weld_attribute_list(request):
    weld_id = request.GET.get("weld_id")
    project_id = request.GET.get("project_id")
    items = models.WeldAttribute.objects.select_related("weld").all().order_by("name")
    if weld_id:
        items = items.filter(weld_id=weld_id)
    if project_id:
        items = items.filter(weld__project_id=project_id)
    return render(request, "weld_attributes/list.html", {"items": items})


@login_required
def weld_attribute_detail(request, pk):
    item = get_object_or_404(models.WeldAttribute, pk=pk)
    return render(request, "weld_attributes/detail.html", {"item": item})


@login_required
def weld_attribute_create(request):
    weld_id = request.GET.get("weld_id")
    if request.method == "POST":
        form = WeldAttributeForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("weld_attribute_detail", pk=item.pk)
    else:
        form = WeldAttributeForm(initial={"weld": weld_id} if weld_id else None)
    return render(request, "weld_attributes/form.html", {"form": form, "title": "New attribute"})


@login_required
def weld_attribute_edit(request, pk):
    item = get_object_or_404(models.WeldAttribute, pk=pk)
    if request.method == "POST":
        form = WeldAttributeForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("weld_attribute_detail", pk=item.pk)
    else:
        form = WeldAttributeForm(instance=item)
    return render(request, "weld_attributes/form.html", {"form": form, "title": "Edit attribute"})


@login_required
def weld_material_list(request):
    weld_id = request.GET.get("weld_id")
    project_id = request.GET.get("project_id")
    items = models.WeldMaterial.objects.select_related("weld", "material").all().order_by("heat_number")
    if weld_id:
        items = items.filter(weld_id=weld_id)
    if project_id:
        items = items.filter(weld__project_id=project_id)
    return render(request, "weld_materials/list.html", {"items": items})


@login_required
def weld_material_detail(request, pk):
    item = get_object_or_404(models.WeldMaterial, pk=pk)
    return render(request, "weld_materials/detail.html", {"item": item})


@login_required
def weld_material_create(request):
    weld_id = request.GET.get("weld_id")
    if request.method == "POST":
        form = WeldMaterialForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("weld_material_detail", pk=item.pk)
    else:
        form = WeldMaterialForm(initial={"weld": weld_id} if weld_id else None)
    return render(request, "weld_materials/form.html", {"form": form, "title": "New material"})


@login_required
def weld_material_edit(request, pk):
    item = get_object_or_404(models.WeldMaterial, pk=pk)
    if request.method == "POST":
        form = WeldMaterialForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("weld_material_detail", pk=item.pk)
    else:
        form = WeldMaterialForm(instance=item)
    return render(request, "weld_materials/form.html", {"form": form, "title": "Edit material"})


@login_required
def weld_consumable_list(request):
    weld_id = request.GET.get("weld_id")
    project_id = request.GET.get("project_id")
    items = models.WeldConsumable.objects.select_related("weld", "consumable").all().order_by("batch")
    if weld_id:
        items = items.filter(weld_id=weld_id)
    if project_id:
        items = items.filter(weld__project_id=project_id)
    return render(request, "weld_consumables/list.html", {"items": items})


@login_required
def weld_consumable_detail(request, pk):
    item = get_object_or_404(models.WeldConsumable, pk=pk)
    return render(request, "weld_consumables/detail.html", {"item": item})


@login_required
def weld_consumable_create(request):
    weld_id = request.GET.get("weld_id")
    if request.method == "POST":
        form = WeldConsumableForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("weld_consumable_detail", pk=item.pk)
    else:
        form = WeldConsumableForm(initial={"weld": weld_id} if weld_id else None)
    return render(request, "weld_consumables/form.html", {"form": form, "title": "New consumable"})


@login_required
def weld_consumable_edit(request, pk):
    item = get_object_or_404(models.WeldConsumable, pk=pk)
    if request.method == "POST":
        form = WeldConsumableForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("weld_consumable_detail", pk=item.pk)
    else:
        form = WeldConsumableForm(instance=item)
    return render(request, "weld_consumables/form.html", {"form": form, "title": "Edit consumable"})


@login_required
def visual_inspection_list(request):
    weld_id = request.GET.get("weld_id")
    project_id = request.GET.get("project_id")
    stage = request.GET.get("stage")
    items = models.VisualInspection.objects.select_related("weld", "inspector").all().order_by("-at")
    if weld_id:
        items = items.filter(weld_id=weld_id)
    if project_id:
        items = items.filter(weld__project_id=project_id)
    if stage:
        items = items.filter(stage=stage)
    return render(request, "visual_inspections/list.html", {"items": items})


@login_required
def visual_inspection_detail(request, pk):
    item = get_object_or_404(models.VisualInspection, pk=pk)
    return render(request, "visual_inspections/detail.html", {"item": item})


@login_required
def visual_inspection_create(request):
    weld_id = request.GET.get("weld_id")
    if request.method == "POST":
        form = VisualInspectionForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("visual_inspection_detail", pk=item.pk)
    else:
        form = VisualInspectionForm(initial={"weld": weld_id} if weld_id else None)
    return render(request, "visual_inspections/form.html", {"form": form, "title": "New inspection"})


@login_required
def visual_inspection_edit(request, pk):
    item = get_object_or_404(models.VisualInspection, pk=pk)
    if request.method == "POST":
        form = VisualInspectionForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("visual_inspection_detail", pk=item.pk)
    else:
        form = VisualInspectionForm(instance=item)
    return render(request, "visual_inspections/form.html", {"form": form, "title": "Edit inspection"})
