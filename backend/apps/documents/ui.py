from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import DocumentForm


@login_required
def document_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    items = models.Document.objects.select_related("project").all().order_by("title")
    if q:
        items = items.filter(title__icontains=q)
    if project_id:
        items = items.filter(project_id=project_id)
    return render(request, "documents/list.html", {"items": items})


@login_required
def document_detail(request, pk):
    item = get_object_or_404(models.Document, pk=pk)
    return render(request, "documents/detail.html", {"item": item})


@login_required
def document_create(request):
    if request.method == "POST":
        form = DocumentForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("document_detail", pk=item.pk)
    else:
        form = DocumentForm()
    return render(request, "documents/form.html", {"form": form, "title": "Nuevo documento"})


@login_required
def document_edit(request, pk):
    item = get_object_or_404(models.Document, pk=pk)
    if request.method == "POST":
        form = DocumentForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("document_detail", pk=item.pk)
    else:
        form = DocumentForm(instance=item)
    return render(request, "documents/form.html", {"form": form, "title": "Editar documento"})
