from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from . import models
from .forms import WpqForm


@login_required
def wpq_list(request):
    q = request.GET.get("q")
    project_id = request.GET.get("project_id")
    items = models.Wpq.objects.select_related("welder").all().order_by("code")
    if q:
        items = items.filter(code__icontains=q)
    if project_id:
        items = items.filter(welder__continuitylog__weld__project_id=project_id).distinct()
    return render(request, "wpq/list.html", {"items": items})


@login_required
def wpq_detail(request, pk):
    item = get_object_or_404(models.Wpq, pk=pk)
    return render(request, "wpq/detail.html", {"item": item})


@login_required
def wpq_create(request):
    if request.method == "POST":
        form = WpqForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect("wpq_detail", pk=item.pk)
    else:
        form = WpqForm()
    return render(request, "wpq/form.html", {"form": form, "title": "New WPQ"})


@login_required
def wpq_edit(request, pk):
    item = get_object_or_404(models.Wpq, pk=pk)
    if request.method == "POST":
        form = WpqForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("wpq_detail", pk=item.pk)
    else:
        form = WpqForm(instance=item)
    return render(request, "wpq/form.html", {"form": form, "title": "Edit WPQ"})
