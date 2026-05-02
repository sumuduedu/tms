from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssignStudentForm, BatchForm
from .models import Batch


def _is_admin_or_staff(user):
    return user.is_superuser or user.is_staff


@login_required
def batch_list(request):
    if not _is_admin_or_staff(request.user):
        raise PermissionDenied
    batches = Batch.objects.select_related("course", "teacher").prefetch_related("students")
    return render(request, "batch/batch_list.html", {"batches": batches})


@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(
        Batch.objects.select_related("course", "teacher").prefetch_related("students"),
        pk=pk,
    )
    user = request.user
    if _is_admin_or_staff(user):
        pass
    elif getattr(user, "role", None) == "teacher" and batch.teacher_id == user.id:
        pass
    elif getattr(user, "role", None) == "student" and batch.students.filter(id=user.id).exists():
        pass
    else:
        raise PermissionDenied
    return render(request, "batch/batch_detail.html", {"batch": batch})


@login_required
def batch_create(request):
    if not _is_admin_or_staff(request.user):
        raise PermissionDenied
    form = BatchForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Batch created successfully.")
        return redirect("batch_list")
    return render(request, "batch/batch_form.html", {"form": form, "title": "Create Batch"})


@login_required
def batch_update(request, pk):
    if not _is_admin_or_staff(request.user):
        raise PermissionDenied
    batch = get_object_or_404(Batch, pk=pk)
    form = BatchForm(request.POST or None, instance=batch)
    if form.is_valid():
        form.save()
        messages.success(request, "Batch updated successfully.")
        return redirect("batch_detail", pk=batch.pk)
    return render(request, "batch/batch_form.html", {"form": form, "title": "Update Batch"})


@login_required
def batch_delete(request, pk):
    if not _is_admin_or_staff(request.user):
        raise PermissionDenied
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == "POST":
        batch.delete()
        messages.success(request, "Batch deleted successfully.")
        return redirect("batch_list")
    return render(request, "batch/batch_detail.html", {"batch": batch, "confirm_delete": True})


@login_required
def assign_students_to_batch(request, pk):
    if not _is_admin_or_staff(request.user):
        raise PermissionDenied
    batch = get_object_or_404(Batch, pk=pk)
    form = AssignStudentForm(request.POST or None, batch=batch)
    if form.is_valid():
        form.save()
        messages.success(request, "Students assigned successfully.")
        return redirect("batch_detail", pk=batch.pk)
    return render(request, "batch/assign_students.html", {"batch": batch, "form": form})


@login_required
def my_batches(request):
    if getattr(request.user, "role", None) != "teacher":
        raise PermissionDenied
    batches = Batch.objects.filter(teacher=request.user).select_related("course").prefetch_related("students")
    return render(request, "batch/batch_list.html", {"batches": batches, "teacher_view": True})


@login_required
def student_batch_view(request):
    if getattr(request.user, "role", None) != "student":
        raise PermissionDenied
    batches = Batch.objects.filter(students=request.user).select_related("course", "teacher")
    return render(request, "batch/batch_list.html", {"batches": batches, "student_view": True})
