from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import WpsForm


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
    return render(request, "wps/detail.html", {"item": item})


@login_required
def wps_create(request):
    if request.method == "POST":
        form = WpsForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("wps_detail", pk=item.pk)
    else:
        form = WpsForm()
    return render(request, "wps/form.html", {"form": form, "title": "Nuevo WPS"})


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
    return render(request, "wps/form.html", {"form": form, "title": "Editar WPS"})
