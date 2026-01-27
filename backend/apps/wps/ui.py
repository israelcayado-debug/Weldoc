from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import WpsForm, WpsProcessForm, WpsVariableBulkForm


@login_required
def wps_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    items = models.Wps.objects.all().order_by("code")
    if q:
        items = items.filter(code__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
    return render(request, "wps/list.html", {"items": items})


@login_required
def wps_detail(request, pk):
    item = get_object_or_404(models.Wps, pk=pk)
    processes = models.WpsProcess.objects.filter(wps=item).order_by("order", "process_code")
    return render(
        request,
        "wps/detail.html",
        {"item": item, "processes": processes},
    )


@login_required
def wps_create(request):
    if request.method == "POST":
        form = WpsForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("wps_detail", pk=item.pk)
    else:
        form = WpsForm()
    return render(request, "wps/form.html", {"form": form, "title": "New WPS"})


@login_required
def wps_edit(request, pk):
    item = get_object_or_404(models.Wps, pk=pk)
    if request.method == "POST":
        form = WpsForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("wps_detail", pk=item.pk)
    else:
        form = WpsForm(instance=item)
    return render(request, "wps/form.html", {"form": form, "title": "Edit WPS"})


@login_required
def wps_qw482_form(request, pk):
    wps = get_object_or_404(models.Wps, pk=pk)
    processes = list(models.WpsProcess.objects.filter(wps=wps).order_by("order", "process_code"))
    if not processes:
        return render(
            request,
            "wps/qw482_form.html",
            {"wps": wps, "processes": [], "sections": [], "errors": {"__all__": "Add at least one process."}},
        )

    sections = [
        ("QW-402", "Joints (QW-402)"),
        ("QW-403", "Base Metals (QW-403)"),
        ("QW-404", "Filler Metals (QW-404)"),
        ("QW-405", "Positions (QW-405)"),
        ("QW-406", "Preheat (QW-406)"),
        ("QW-407", "PWHT (QW-407)"),
        ("QW-408", "Gas (QW-408)"),
        ("QW-409", "Electrical Characteristics (QW-409)"),
        ("QW-410", "Technique (QW-410)"),
    ]

    def defs_for(process):
        return models.WpsVariableDefinition.objects.filter(
            process_code=process.process_code
        ).filter(
            Q(special_process__isnull=True)
            | Q(special_process="")
            | Q(special_process=process.special_process)
        )

    defs_by_process = {
        process.id: list(defs_for(process).order_by("category", "code"))
        for process in processes
    }
    values = {
        (v.wps_process_id, v.definition_id): v
        for v in models.WpsVariableValue.objects.filter(wps_process__in=processes)
    }

    required_defs = set()
    for process in processes:
        for definition in defs_by_process[process.id]:
            if definition.category == "essential":
                required_defs.add((process.id, definition.id))
            if definition.category == "supplementary" and wps.impact_test:
                required_defs.add((process.id, definition.id))

    errors = {}
    if request.method == "POST":
        for process in processes:
            for definition in defs_by_process[process.id]:
                field_name = f"val_{process.id}_{definition.id}"
                raw_value = request.POST.get(field_name, "")
                if (process.id, definition.id) in required_defs and not str(raw_value).strip():
                    errors[field_name] = "Required."
                    continue
                key = (process.id, definition.id)
                if raw_value is None:
                    raw_value = ""
                raw_value = str(raw_value)
                item = values.get(key)
                if item:
                    if item.value != raw_value or item.unit != (definition.unit or ""):
                        item.value = raw_value
                        item.unit = definition.unit
                        item.save(update_fields=["value", "unit"])
                elif raw_value.strip():
                    models.WpsVariableValue.objects.create(
                        wps_process=process,
                        definition=definition,
                        value=raw_value,
                        unit=definition.unit,
                    )
        if not errors:
            return redirect("wps_detail", pk=wps.pk)

    sections_data = []
    for code, title in sections:
        defs = []
        for process in processes:
            defs.extend([d for d in defs_by_process[process.id] if (d.paragraph or "").startswith(code)])
        seen = set()
        unique_defs = []
        for definition in defs:
            if definition.id in seen:
                continue
            seen.add(definition.id)
            unique_defs.append(definition)
        rows = []
        for definition in unique_defs:
            cells = []
            for process in processes:
                field_name = f"val_{process.id}_{definition.id}"
                item = values.get((process.id, definition.id))
                cells.append(
                    {
                        "field_name": field_name,
                        "value": item.value if item else "",
                        "error": errors.get(field_name),
                    }
                )
            rows.append(
                {
                    "definition": definition,
                    "cells": cells,
                    "required": any(
                        (process.id, definition.id) in required_defs for process in processes
                    ),
                }
            )
        section_payload = {
            "code": code,
            "title": title,
            "rows": rows,
        }
        if code == "QW-409":
            process_rows = []
            for index, process in enumerate(processes):
                process_cells = [row["cells"][index] for row in rows]
                process_rows.append({"process": process, "cells": process_cells})
            section_payload["process_rows"] = process_rows
        sections_data.append(section_payload)

    return render(
        request,
        "wps/qw482_form.html",
        {
            "wps": wps,
            "processes": processes,
            "sections": sections_data,
            "errors": errors,
            "errors_all": errors.get("__all__"),
        },
    )


@login_required
def wps_process_list(request, pk):
    wps = get_object_or_404(models.Wps, pk=pk)
    processes = models.WpsProcess.objects.filter(wps=wps).order_by("order", "process_code")
    return render(
        request,
        "wps/process_list.html",
        {"wps": wps, "processes": processes},
    )


@login_required
def wps_process_create(request, pk):
    wps = get_object_or_404(models.Wps, pk=pk)
    if request.method == "POST":
        form = WpsProcessForm(request.POST)
        if form.is_valid():
            process = form.save()
            return redirect("wps_process_list", pk=wps.pk)
    else:
        next_order = models.WpsProcess.objects.filter(wps=wps).count() + 1
        form = WpsProcessForm(initial={"wps": wps, "order": next_order})
    return render(
        request,
        "wps/process_form.html",
        {"form": form, "wps": wps, "title": "Add process"},
    )


@login_required
def wps_process_edit(request, process_id):
    process = get_object_or_404(models.WpsProcess, pk=process_id)
    wps = process.wps
    if request.method == "POST":
        form = WpsProcessForm(request.POST, instance=process)
        if form.is_valid():
            form.save()
            return redirect("wps_process_list", pk=wps.pk)
    else:
        form = WpsProcessForm(instance=process)
    return render(
        request,
        "wps/process_form.html",
        {"form": form, "wps": wps, "title": "Edit process"},
    )


@login_required
def wps_process_variables(request, process_id):
    process = get_object_or_404(models.WpsProcess, pk=process_id)
    wps = process.wps
    definitions = models.WpsVariableDefinition.objects.filter(
        process_code=process.process_code
    ).filter(
        Q(special_process__isnull=True) | Q(special_process="") | Q(special_process=process.special_process)
    ).order_by("category", "code")
    required_ids = []
    for definition in definitions:
        if definition.category == "essential":
            required_ids.append(definition.id)
        if definition.category == "supplementary" and wps.impact_test:
            required_ids.append(definition.id)
    existing = {
        v.definition_id: v for v in models.WpsVariableValue.objects.filter(wps_process=process)
    }
    if request.method == "POST":
        form = WpsVariableBulkForm(definitions, required_ids=required_ids, data=request.POST)
        if form.is_valid():
            for definition in definitions:
                field_name = f"var_{definition.id}"
                raw_value = form.cleaned_data.get(field_name)
                value = "" if raw_value is None else str(raw_value)
                item = existing.get(definition.id)
                if item:
                    item.value = value
                    if definition.unit:
                        item.unit = definition.unit
                    item.save(update_fields=["value", "unit"])
                elif value:
                    models.WpsVariableValue.objects.create(
                        wps_process=process,
                        definition=definition,
                        value=value,
                        unit=definition.unit,
                    )
            return redirect("wps_detail", pk=wps.pk)
    else:
        initial = {}
        for definition in definitions:
            item = existing.get(definition.id)
            if item:
                initial[f"var_{definition.id}"] = item.value
        form = WpsVariableBulkForm(definitions, required_ids=required_ids, initial=initial)
    return render(
        request,
        "wps/process_variables.html",
        {"form": form, "process": process, "wps": wps, "definitions": definitions},
    )
