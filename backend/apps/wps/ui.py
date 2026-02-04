from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import models
from .forms import (
    PqrQuickCreateForm,
    PqrScanUploadForm,
    WpsForm,
    WpsProcessForm,
    WpsQuickCreateForm,
    WpsVariableBulkForm,
)


def _next_copy_code(wps):
    base = f"{wps.code}-COPY"
    candidate = base
    index = 2
    while models.Wps.objects.filter(project=wps.project, code=candidate).exists():
        candidate = f"{base}-{index}"
        index += 1
    return candidate


def _result_value(result_map, *keys):
    for key in keys:
        value = result_map.get(key)
        if value:
            return value
    return "-"


@login_required
def wps_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    items = (
        models.Wps.objects.select_related("project")
        .prefetch_related(
            "wpspqrlink_set__pqr",
            "wpsvariable_set",
            "wpsprocess_set__wpsvariablevalue_set__definition",
        )
        .order_by("code")
    )
    if q:
        items = items.filter(code__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
    for item in items:
        p_numbers = set()
        for variable in item.wpsvariable_set.all():
            key = (variable.name or "").lower()
            if key in {
                "material_pno",
                "p_number",
                "p_no",
                "p_numbers",
                "p_number_qualified",
                "p_no_qualified",
            }:
                value = (variable.value or "").strip()
                if value:
                    p_numbers.add(value)
        for process in item.wpsprocess_set.all():
            for variable_value in process.wpsvariablevalue_set.all():
                definition = variable_value.definition
                name = (definition.name or "").lower()
                label = (definition.label or "").lower()
                if "p_no" in name or "p_number" in name or "p-no" in label or "p-number" in label:
                    value = (variable_value.value or "").strip()
                    if value:
                        p_numbers.add(value)
        item.display_p_numbers = ", ".join(sorted(p_numbers)) if p_numbers else "-"
        pqr_codes = sorted(
            {link.pqr.code for link in item.wpspqrlink_set.all() if link.pqr_id}
        )
        item.display_pqrs = ", ".join(pqr_codes) if pqr_codes else "-"
    return render(request, "wps/list.html", {"items": items})


@login_required
@require_POST
def wps_copy(request, pk):
    source = get_object_or_404(models.Wps, pk=pk)
    process_map = {}
    with transaction.atomic():
        copied = models.Wps.objects.create(
            project=source.project,
            code=_next_copy_code(source),
            standard=source.standard,
            impact_test=source.impact_test,
            status="draft",
        )
        for process in models.WpsProcess.objects.filter(wps=source).order_by("order"):
            process_map[process.id] = models.WpsProcess.objects.create(
                wps=copied,
                process_code=process.process_code,
                special_process=process.special_process,
                order=process.order,
            )
        for value in models.WpsVariableValue.objects.filter(wps_process__wps=source):
            target_process = process_map.get(value.wps_process_id)
            if not target_process:
                continue
            models.WpsVariableValue.objects.create(
                wps_process=target_process,
                definition=value.definition,
                value=value.value,
                unit=value.unit,
            )
        for variable in models.WpsVariable.objects.filter(wps=source):
            models.WpsVariable.objects.create(
                wps=copied,
                name=variable.name,
                value=variable.value,
                unit=variable.unit,
            )
    return redirect("wps_qw482_form", pk=copied.pk)


@login_required
def pqr_list(request):
    q = request.GET.get("q")
    items = (
        models.Pqr.objects.select_related("project")
        .prefetch_related("pqrresult_set")
        .order_by("code")
    )
    if q:
        items = items.filter(code__icontains=q)
    for item in items:
        result_map = {row.test_type: row.result for row in item.pqrresult_set.all()}
        item.display_process = _result_value(result_map, "processes", "process")
        item.display_thickness = _result_value(result_map, "thickness_range", "thickness")
        item.display_p_no = _result_value(result_map, "material_pno", "p_no")
        item.display_f_gtaw = _result_value(result_map, "filler_fno_gtaw", "filler_fno")
        item.display_a_gtaw = _result_value(result_map, "a_no_gtaw")
        item.display_f_smaw = _result_value(result_map, "filler_fno_smaw")
        item.display_a_smaw = _result_value(result_map, "a_no_smaw")
        item.display_t_max_gtaw = _result_value(result_map, "t_max_gtaw")
        item.display_t_max_smaw = _result_value(result_map, "t_max_smaw")
        item.display_gtaw_filler_form = _result_value(
            result_map,
            "gtaw_filler_form",
            "filler_form_gtaw",
            "filler_and_form_gtaw",
        )
        item.display_preheat = _result_value(result_map, "preheat")
        item.display_pwht = _result_value(result_map, "pwht")
        item.display_gas_protection = _result_value(result_map, "gas_protection")
        item.display_aws_sfa_gtaw = _result_value(result_map, "aws_sfa_gtaw")
        item.display_aws_sfa_smaw = _result_value(result_map, "aws_sfa_smaw")
        item.display_interpass_temp = _result_value(result_map, "interpass_temp")
        item.display_heat_input_gtaw = _result_value(result_map, "heat_input_gtaw")
        item.display_heat_input_smaw = _result_value(result_map, "heat_input_smaw")
        item.display_base_metal_a_no = _result_value(result_map, "base_metal_a_no")
        item.display_position = _result_value(result_map, "position")
        item.display_gas_backing = _result_value(result_map, "gas_backing")
    return render(request, "wps/pqr_list.html", {"items": items})


@login_required
def pqr_detail(request, pk):
    item = get_object_or_404(models.Pqr, pk=pk)
    results = models.PqrResult.objects.filter(pqr=item).order_by("test_type")
    upload_form = PqrScanUploadForm()
    return render(
        request,
        "wps/pqr_detail.html",
        {"item": item, "results": results, "upload_form": upload_form},
    )


@login_required
@require_POST
def pqr_upload_scan(request, pk):
    item = get_object_or_404(models.Pqr, pk=pk)
    form = PqrScanUploadForm(request.POST, request.FILES)
    if form.is_valid():
        item.scanned_pdf = form.cleaned_data["scan_pdf"]
        item.save(update_fields=["scanned_pdf"])
        return redirect("pqr_detail", pk=item.pk)
    results = models.PqrResult.objects.filter(pqr=item).order_by("test_type")
    return render(
        request,
        "wps/pqr_detail.html",
        {"item": item, "results": results, "upload_form": form},
        status=400,
    )


@login_required
def pqr_create_tool(request):
    if request.method == "POST":
        form = PqrQuickCreateForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("pqr_detail", pk=item.pk)
    else:
        form = PqrQuickCreateForm()
    return render(
        request,
        "wps/pqr_create_tool.html",
        {"form": form, "title": "PQR Creation Tool"},
    )


@login_required
@require_POST
def pqr_submit_review(request, pk):
    item = get_object_or_404(models.Pqr, pk=pk)
    if item.status == "draft":
        item.status = "in_review"
        item.save(update_fields=["status"])
    return redirect("pqr_detail", pk=item.pk)


@login_required
@require_POST
def pqr_approve(request, pk):
    item = get_object_or_404(models.Pqr, pk=pk)
    has_results = models.PqrResult.objects.filter(pqr=item).exists()
    if item.status in ("draft", "in_review") and has_results:
        item.status = "approved"
        item.save(update_fields=["status"])
    return redirect("pqr_detail", pk=item.pk)


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
def wps_create_tool(request):
    if request.method == "POST":
        form = WpsQuickCreateForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("wps_qw482_form", pk=item.pk)
    else:
        form = WpsQuickCreateForm()
    return render(
        request,
        "wps/create_tool.html",
        {"form": form, "title": "WPS Creation Tool"},
    )


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
