from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
import re
import uuid

from apps.projects import models as project_models
from apps.users import models as user_models

from . import models
from .forms import (
    PqrQuickCreateForm,
    PqrScanUploadForm,
    WpsForm,
    WpsProcessForm,
    WpsQuickCreateForm,
    WpsVariableBulkForm,
)


EDITOR_PREFIX = "editor.tab1."
EDITOR_FIELDS = [
    "supporting_pqr",
    "pqr_date",
    "reference_code",
    "imperial_enabled",
    "welding_process_gtaw",
    "welding_process_smaw",
    "welding_process_gmaw",
    "welding_process_saw",
    "welding_process_spray",
    "welding_process_short_arc",
    "welding_type_manual",
    "welding_type_semiautomatic",
    "welding_type_automatic",
    "welding_type_others",
    "backing",
    "backing_processes",
    "base_material_1_spec",
    "base_material_1_p_no",
    "base_material_1_group_no",
    "base_material_2_spec",
    "base_material_2_p_no",
    "base_material_2_group_no",
    "chemical_analysis_1",
    "chemical_analysis_2",
    "thickness_range_groove",
    "thickness_range_fillet",
    "pipe_diameter_range_groove",
    "pipe_diameter_range_fillet",
    "flux_trade_name",
    "flux_type",
    "flux_class",
    "max_deposit_gtaw",
    "max_deposit_other",
    "supplemental_filler",
    "consumable_inert",
    "preheat_thickness",
    "preheat_temperature",
    "max_interpass_temp",
    "preheat_maintenance",
    "immediate_postheating",
    "preheating_method",
    "checked_by",
    "others_preheat",
    "pwht_temp_range",
    "pwht_time_range",
    "pwht_heating_rate",
    "pwht_cooling_rate",
    "pwht_other",
    "gas_shielding",
    "gas_percent",
    "gas_flow",
    "gas_backing",
    "trailing_gas",
    "current_type",
    "polarity",
    "pulsed_current",
    "gmaw_transfer_mode",
    "tungsten_type",
    "tungsten_size",
    "electrode_wire_feed_speed",
    "technique_string_bead",
    "technique_wave_bead",
    "technique_orifice_cup_size",
    "technique_gas_cup_size",
    "technique_cleaning_brushing",
    "technique_cleaning_grinding",
    "technique_cleaning_chipping",
    "technique_cleaning_other",
    "technique_back_gouging_grinding",
    "technique_back_gouging_chipping",
    "technique_back_gouging_machining",
    "technique_back_gouging_peening",
    "technique_back_gouging_other",
    "technique_contact_tube_distance",
    "technique_oscillation",
    "technique_passes_per_side",
    "technique_electrodes",
    "technique_travel_speed_range",
    "technique_other",
    "technique_electrode_spacing",
    "technique_thermal_processes",
    "tack_welding_wps_no",
    "tack_welding_pass_no",
    "tack_welding_bead_length_min_mm",
    "tack_welding_min_passes_required",
    "tack_welding_note_1",
    "tack_welding_note_2",
    "welding_data_notes",
]
for i in range(1, 5):
    EDITOR_FIELDS.extend(
        [
            f"process_line_{i}_process",
            f"process_line_{i}_f_no",
            f"process_line_{i}_a_no",
            f"process_line_{i}_spec_sfa",
            f"process_line_{i}_aws_class",
            f"process_line_{i}_size_mm",
            f"process_line_{i}_thickness_groove",
            f"process_line_{i}_thickness_fillet",
        ]
    )
for i in range(1, 7):
    EDITOR_FIELDS.extend(
        [
            f"sequence_block_{i}_enabled",
            f"sequence_block_{i}_position",
            f"sequence_block_{i}_progress_uphill",
            f"sequence_block_{i}_image",
        ]
    )


PROCESS_LINE_RE = re.compile(r"^process_line_(\d+)_(process|f_no|a_no|spec_sfa|aws_class|size_mm|thickness_groove|thickness_fillet)$")
WELDING_DATA_LINE_RE = re.compile(
    r"^welding_data_line_(\d+)_(weld_layer|process|filler_metal|diameter_mm|amp_range|volt_range|travel_speed|max_heat_input|shielding_gas)$"
)


def _editor_value_map(wps):
    rows = models.WpsVariable.objects.filter(
        wps=wps, name__startswith=EDITOR_PREFIX
    ).values_list("name", "value")
    return {name[len(EDITOR_PREFIX):]: value for name, value in rows}


def _extract_editor_payload(post_data):
    payload = {}
    for field in EDITOR_FIELDS:
        payload[field] = (post_data.get(field) or "").strip()
    payload["imperial_enabled"] = "1" if post_data.get("imperial_enabled") else "0"
    for key in post_data.keys():
        match = PROCESS_LINE_RE.match(key)
        if match:
            payload[key] = (post_data.get(key) or "").strip()
            continue
        match = WELDING_DATA_LINE_RE.match(key)
        if match:
            payload[key] = (post_data.get(key) or "").strip()
    return payload


def _save_editor_payload(wps, payload):
    existing = {
        item.name: item
        for item in models.WpsVariable.objects.filter(
            wps=wps,
            name__startswith=EDITOR_PREFIX,
        )
    }
    payload_keys = set(EDITOR_FIELDS)
    payload_keys.update(
        key for key in payload.keys() if PROCESS_LINE_RE.match(key)
    )
    payload_keys.update(
        key for key in payload.keys() if WELDING_DATA_LINE_RE.match(key)
    )
    for field in sorted(payload_keys):
        key = f"{EDITOR_PREFIX}{field}"
        value = payload.get(field, "")
        item = existing.pop(key, None)
        if item:
            if item.value != value:
                item.value = value
                item.save(update_fields=["value"])
        else:
            models.WpsVariable.objects.create(wps=wps, name=key, value=value)
    for leftover in existing.values():
        leftover.delete()


def _build_process_rows(values):
    indexes = set()
    for key in values.keys():
        match = PROCESS_LINE_RE.match(key)
        if match:
            indexes.add(int(match.group(1)))
    if not indexes:
        indexes = {1}
    rows = []
    for idx in sorted(indexes):
        rows.append(
            {
                "idx": idx,
                "process": values.get(f"process_line_{idx}_process", ""),
                "f_no": values.get(f"process_line_{idx}_f_no", ""),
                "a_no": values.get(f"process_line_{idx}_a_no", ""),
                "spec_sfa": values.get(f"process_line_{idx}_spec_sfa", ""),
                "aws_class": values.get(f"process_line_{idx}_aws_class", ""),
                "size_mm": values.get(f"process_line_{idx}_size_mm", ""),
                "thickness_groove": values.get(f"process_line_{idx}_thickness_groove", ""),
                "thickness_fillet": values.get(f"process_line_{idx}_thickness_fillet", ""),
            }
        )
    return rows


def _build_welding_data_rows(values):
    indexes = set()
    for key in values.keys():
        match = WELDING_DATA_LINE_RE.match(key)
        if match:
            indexes.add(int(match.group(1)))
    if not indexes:
        indexes = {1}
    rows = []
    for idx in sorted(indexes):
        rows.append(
            {
                "idx": idx,
                "weld_layer": values.get(f"welding_data_line_{idx}_weld_layer", ""),
                "process": values.get(f"welding_data_line_{idx}_process", ""),
                "filler_metal": values.get(f"welding_data_line_{idx}_filler_metal", ""),
                "diameter_mm": values.get(f"welding_data_line_{idx}_diameter_mm", ""),
                "amp_range": values.get(f"welding_data_line_{idx}_amp_range", ""),
                "volt_range": values.get(f"welding_data_line_{idx}_volt_range", ""),
                "travel_speed": values.get(f"welding_data_line_{idx}_travel_speed", ""),
                "max_heat_input": values.get(f"welding_data_line_{idx}_max_heat_input", ""),
                "shielding_gas": values.get(f"welding_data_line_{idx}_shielding_gas", ""),
            }
        )
    return rows


def _save_sheet2_sketch_uploads(payload, post_data, files, wps):
    for idx in range(1, 7):
        value_key = f"sequence_block_{idx}_image"
        file_key = f"sequence_block_{idx}_image_file"
        clear_key = f"sequence_block_{idx}_image_clear"
        if post_data.get(clear_key):
            payload[value_key] = ""
            continue
        upload = files.get(file_key)
        if not upload:
            continue
        suffix = ""
        name = getattr(upload, "name", "")
        if "." in name:
            suffix = "." + name.rsplit(".", 1)[1].lower()
        if not suffix:
            suffix = ".png"
        storage_path = (
            f"wps_sheets/{wps.id}/sequence_block_{idx}_{uuid.uuid4().hex}{suffix}"
        )
        payload[value_key] = default_storage.save(storage_path, upload)


def _build_sequence_blocks(values):
    enabled_map = {}
    has_enabled_flags = False
    for idx in range(1, 7):
        raw = (values.get(f"sequence_block_{idx}_enabled") or "").strip()
        if raw in {"0", "1"}:
            has_enabled_flags = True
        enabled_map[idx] = raw == "1"
    if not has_enabled_flags:
        raw_count = (values.get("sequence_block_count") or "1").strip()
        try:
            count = int(raw_count)
        except (TypeError, ValueError):
            count = 1
        count = max(1, min(6, count))
        for idx in range(1, 7):
            enabled_map[idx] = idx <= count
    if not any(enabled_map.values()):
        enabled_map[1] = True

    count = sum(1 for idx in range(1, 7) if enabled_map[idx])
    blocks = []
    for idx in range(1, 7):
        image_path = values.get(f"sequence_block_{idx}_image", "")
        image_url = ""
        if image_path:
            try:
                image_url = default_storage.url(image_path)
            except Exception:
                image_url = image_path
        blocks.append(
            {
                "idx": idx,
                "visible": enabled_map[idx],
                "enabled": "1" if enabled_map[idx] else "0",
                "position": values.get(f"sequence_block_{idx}_position", ""),
                "progress_uphill": values.get(
                    f"sequence_block_{idx}_progress_uphill", ""
                ),
                "image_path": image_path,
                "image_url": image_url,
            }
        )
    return count, blocks


def _resolve_supporting_pqr_display(wps, payload):
    selected = (payload.get("supporting_pqr") or "").strip()
    if selected:
        return selected
    first_link = models.WpsPqrLink.objects.filter(wps=wps).select_related("pqr").first()
    if first_link and first_link.pqr:
        return str(first_link.pqr.id)
    return "HOLD"


def _upsert_supporting_pqr_link(wps, supporting_pqr):
    models.WpsPqrLink.objects.filter(wps=wps).delete()
    if not supporting_pqr or supporting_pqr == "HOLD":
        return
    pqr = models.Pqr.objects.filter(id=supporting_pqr).first()
    if pqr:
        models.WpsPqrLink.objects.create(wps=wps, pqr=pqr)


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


def _resolve_app_user(request):
    email = getattr(request.user, "email", None) or getattr(request.user, "username", None)
    if not email:
        return None
    return user_models.User.objects.filter(email=email).first()


def _status_label(status):
    mapping = {
        models.Wps.STATUS_DRAFT: "Draft",
        models.Wps.STATUS_PENDING_APPROVAL: "Pending approval",
        models.Wps.STATUS_REVIEWED: "Reviewed",
        models.Wps.STATUS_APPROVED: "Approved",
        models.Wps.STATUS_ARCHIVED: "Archived",
    }
    return mapping.get(status, status)


def _get_revision_family_queryset(wps):
    root = wps.root_wps or wps
    return models.Wps.objects.filter(Q(id=root.id) | Q(root_wps=root))


def _next_revision_number(wps):
    family = _get_revision_family_queryset(wps)
    last = family.order_by("-revision_number").first()
    if not last:
        return 0
    return int(last.revision_number or 0) + 1


@login_required
def wps_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    equipment_id = request.GET.get("equipment_id")
    items = (
        models.Wps.objects.select_related("project", "equipment")
        .prefetch_related(
            "wpspqrlink_set__pqr",
            "wpsvariable_set",
            "wpsprocess_set__wpsvariablevalue_set__definition",
        )
        .filter(is_current=True)
        .order_by("code")
    )
    if q:
        items = items.filter(code__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
    if equipment_id:
        items = items.filter(equipment_id=equipment_id)
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
        item.display_revision = f"R{item.revision_number or 0}"
        item.display_status = _status_label(item.status)
    projects = project_models.Project.objects.order_by("name")
    equipment_items = project_models.ProjectEquipment.objects.order_by("name")
    if project_id:
        equipment_items = equipment_items.filter(project_id=project_id)
    return render(
        request,
        "wps/list.html",
        {"items": items, "projects": projects, "equipment_items": equipment_items},
    )


@login_required
@require_POST
def wps_copy(request, pk):
    source = get_object_or_404(models.Wps, pk=pk)
    process_map = {}
    with transaction.atomic():
        copied = models.Wps.objects.create(
            project=source.project,
            equipment=source.equipment,
            code=_next_copy_code(source),
            standard=source.standard,
            impact_test=source.impact_test,
            status=models.Wps.STATUS_DRAFT,
            revision_number=0,
            is_current=True,
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
    return redirect("wps_edit", pk=copied.pk)


@login_required
@require_POST
def wps_delete(request, pk):
    item = get_object_or_404(models.Wps, pk=pk)
    item.delete()
    return redirect("wps_list")


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
    family = _get_revision_family_queryset(item).order_by("-revision_number", "-id")
    current_actor = _resolve_app_user(request)
    can_submit = item.status == models.Wps.STATUS_DRAFT
    can_review = item.status == models.Wps.STATUS_PENDING_APPROVAL
    can_approve = item.status == models.Wps.STATUS_REVIEWED
    if current_actor:
        if can_review and item.submitted_by_id and item.submitted_by_id == current_actor.id:
            can_review = False
        if can_approve and item.reviewed_by_id and item.reviewed_by_id == current_actor.id:
            can_approve = False
        if can_approve and item.submitted_by_id and item.submitted_by_id == current_actor.id:
            can_approve = False
    return render(
        request,
        "wps/detail.html",
        {
            "item": item,
            "revisions": family,
            "can_submit": can_submit,
            "can_review": can_review,
            "can_approve": can_approve,
            "status_label": _status_label(item.status),
        },
    )


@login_required
def wps_create(request):
    if request.method == "POST":
        form = WpsForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            item.status = models.Wps.STATUS_DRAFT
            item.revision_number = 0
            item.is_current = True
            item.save(update_fields=["status", "revision_number", "is_current"])
            payload = _extract_editor_payload(request.POST)
            _save_sheet2_sketch_uploads(payload, request.POST, request.FILES, item)
            supporting_pqr = payload.get("supporting_pqr")
            _upsert_supporting_pqr_link(item, supporting_pqr)
            _save_editor_payload(item, payload)
            return redirect("wps_detail", pk=item.pk)
    else:
        form = WpsForm()
    pqr_items = models.Pqr.objects.select_related("project").order_by("code")
    initial_payload = {}
    if request.method == "POST":
        initial_payload = _extract_editor_payload(request.POST)
    sequence_block_count, sequence_blocks = _build_sequence_blocks(initial_payload)
    active_tab = (
        request.POST.get("active_tab", "tab1")
        if request.method == "POST"
        else "tab1"
    )
    return render(
        request,
        "wps/form.html",
        {
            "form": form,
            "title": "New WPS",
            "tab1": initial_payload,
            "process_rows": _build_process_rows(initial_payload),
            "sequence_block_count": sequence_block_count,
            "sequence_blocks": sequence_blocks,
            "welding_data_rows": _build_welding_data_rows(initial_payload),
            "pqr_items": pqr_items,
            "active_tab": active_tab,
        },
    )


@login_required
def wps_create_tool(request):
    if request.method == "POST":
        form = WpsQuickCreateForm(request.POST)
        if form.is_valid():
            item = form.save()
            item.status = models.Wps.STATUS_DRAFT
            item.revision_number = item.revision_number or 0
            item.is_current = True
            item.save(update_fields=["status", "revision_number", "is_current"])
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
        if item.status != models.Wps.STATUS_DRAFT:
            return redirect("wps_detail", pk=item.pk)
        form = WpsForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            payload = _extract_editor_payload(request.POST)
            _save_sheet2_sketch_uploads(payload, request.POST, request.FILES, item)
            supporting_pqr = payload.get("supporting_pqr")
            _upsert_supporting_pqr_link(item, supporting_pqr)
            _save_editor_payload(item, payload)
            return redirect("wps_detail", pk=item.pk)
    else:
        form = WpsForm(instance=item)
    pqr_items = models.Pqr.objects.select_related("project").order_by("code")
    values = _editor_value_map(item)
    values["supporting_pqr"] = _resolve_supporting_pqr_display(item, values)
    if not values.get("reference_code"):
        values["reference_code"] = item.project.code if item.project else ""
    if values.get("supporting_pqr") == "HOLD":
        values["pqr_date"] = "HOLD"
    if request.method == "POST":
        values = _extract_editor_payload(request.POST)
    sequence_block_count, sequence_blocks = _build_sequence_blocks(values)
    active_tab = (
        request.POST.get("active_tab", "tab1")
        if request.method == "POST"
        else "tab1"
    )
    return render(
        request,
        "wps/form.html",
        {
            "form": form,
            "title": "Edit WPS",
            "tab1": values,
            "process_rows": _build_process_rows(values),
            "sequence_block_count": sequence_block_count,
            "sequence_blocks": sequence_blocks,
            "welding_data_rows": _build_welding_data_rows(values),
            "pqr_items": pqr_items,
            "active_tab": active_tab,
        },
    )


@login_required
@require_POST
def wps_submit_for_approval(request, pk):
    item = get_object_or_404(models.Wps, pk=pk)
    if item.status != models.Wps.STATUS_DRAFT:
        return redirect("wps_detail", pk=item.pk)
    actor = _resolve_app_user(request)
    item.status = models.Wps.STATUS_PENDING_APPROVAL
    item.submitted_by = actor
    item.submitted_at = timezone.now()
    item.reviewed_by = None
    item.reviewed_at = None
    item.approved_by = None
    item.approved_at = None
    item.save(
        update_fields=[
            "status",
            "submitted_by",
            "submitted_at",
            "reviewed_by",
            "reviewed_at",
            "approved_by",
            "approved_at",
        ]
    )
    return redirect("wps_detail", pk=item.pk)


@login_required
@require_POST
def wps_mark_reviewed(request, pk):
    item = get_object_or_404(models.Wps, pk=pk)
    if item.status != models.Wps.STATUS_PENDING_APPROVAL:
        return redirect("wps_detail", pk=item.pk)
    actor = _resolve_app_user(request)
    if actor and item.submitted_by_id and actor.id == item.submitted_by_id:
        return redirect("wps_detail", pk=item.pk)
    item.status = models.Wps.STATUS_REVIEWED
    item.reviewed_by = actor
    item.reviewed_at = timezone.now()
    item.save(update_fields=["status", "reviewed_by", "reviewed_at"])
    return redirect("wps_detail", pk=item.pk)


@login_required
@require_POST
def wps_approve_revision(request, pk):
    item = get_object_or_404(models.Wps, pk=pk)
    if item.status != models.Wps.STATUS_REVIEWED:
        return redirect("wps_detail", pk=item.pk)
    actor = _resolve_app_user(request)
    if actor and item.reviewed_by_id and actor.id == item.reviewed_by_id:
        return redirect("wps_detail", pk=item.pk)
    if actor and item.submitted_by_id and actor.id == item.submitted_by_id:
        return redirect("wps_detail", pk=item.pk)
    item.status = models.Wps.STATUS_APPROVED
    item.approved_by = actor
    item.approved_at = timezone.now()
    item.save(update_fields=["status", "approved_by", "approved_at"])
    return redirect("wps_detail", pk=item.pk)


@login_required
@require_POST
def wps_new_revision(request, pk):
    source = get_object_or_404(models.Wps, pk=pk)
    process_map = {}
    root = source.root_wps or source
    next_revision = _next_revision_number(source)
    with transaction.atomic():
        family = _get_revision_family_queryset(source)
        family.update(is_current=False)
        copied = models.Wps.objects.create(
            project=source.project,
            equipment=source.equipment,
            code=source.code,
            standard=source.standard,
            impact_test=source.impact_test,
            status=models.Wps.STATUS_DRAFT,
            root_wps=root if root.id != source.id or source.root_wps_id else source,
            revision_number=next_revision,
            is_current=True,
            submitted_by=None,
            submitted_at=None,
            reviewed_by=None,
            reviewed_at=None,
            approved_by=None,
            approved_at=None,
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
    return redirect("wps_edit", pk=copied.pk)


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
