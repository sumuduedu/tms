from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssessmentForm, AttendanceForm, ResultForm
from .models import Assessment, Attendance, FinalResult, Result


def _is_teacher(user):
    return user.is_authenticated and user.role == "teacher"


def _is_student(user):
    return user.is_authenticated and user.role == "student"


def _is_admin_or_staff(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff or user.role in {"admin", "staff"})


def _require_teacher_or_admin(user):
    if not (_is_teacher(user) or _is_admin_or_staff(user)):
        raise PermissionDenied


@login_required
def mark_attendance(request, batch_id):
    batch = get_object_or_404(Assessment._meta.get_field("batch").remote_field.model, pk=batch_id)
    _require_teacher_or_admin(request.user)
    if _is_teacher(request.user) and getattr(batch, "teacher_id", None) != request.user.id:
        raise PermissionDenied

    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.batch = batch
            attendance.marked_by = request.user
            attendance.save()
            messages.success(request, "Attendance marked successfully.")
            return redirect("assessment:attendance_list", batch_id=batch.id)
    else:
        form = AttendanceForm()
        if hasattr(batch, "students"):
            form.fields["student"].queryset = batch.students.all()

    return render(request, "assessment/attendance_form.html", {"form": form, "batch": batch})


@login_required
def attendance_list(request, batch_id):
    batch = get_object_or_404(Assessment._meta.get_field("batch").remote_field.model, pk=batch_id)
    qs = Attendance.objects.filter(batch=batch).select_related("student")
    if _is_student(request.user):
        qs = qs.filter(student=request.user)
    return render(request, "assessment/attendance_list.html", {"records": qs, "batch": batch})


@login_required
def assessment_list(request, batch_id):
    batch = get_object_or_404(Assessment._meta.get_field("batch").remote_field.model, pk=batch_id)
    assessments = Assessment.objects.filter(batch=batch)
    return render(request, "assessment/assessment_list.html", {"assessments": assessments, "batch": batch})


@login_required
def assessment_create(request, batch_id):
    batch = get_object_or_404(Assessment._meta.get_field("batch").remote_field.model, pk=batch_id)
    _require_teacher_or_admin(request.user)
    if request.method == "POST":
        form = AssessmentForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.batch = batch
            obj.created_by = request.user
            obj.save()
            return redirect("assessment:assessment_list", batch_id=batch.id)
    else:
        form = AssessmentForm()
    return render(request, "assessment/assessment_form.html", {"form": form, "batch": batch})


@login_required
def assessment_detail(request, id):
    assessment = get_object_or_404(Assessment, pk=id)
    return render(request, "assessment/assessment_detail.html", {"assessment": assessment})


@login_required
@transaction.atomic
def enter_marks(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    _require_teacher_or_admin(request.user)
    if request.method == "POST":
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.assessment = assessment
            result.save()
            messages.success(request, "Marks entered successfully.")
            return redirect("assessment:batch_results", assessment_id=assessment.id)
    else:
        form = ResultForm()
        if hasattr(assessment.batch, "students"):
            form.fields["student"].queryset = assessment.batch.students.all()

    return render(request, "assessment/result_entry.html", {"form": form, "assessment": assessment})


@login_required
def student_results(request):
    if not _is_student(request.user) and not _is_admin_or_staff(request.user):
        raise PermissionDenied
    qs = Result.objects.select_related("assessment", "assessment__batch")
    if _is_student(request.user):
        qs = qs.filter(student=request.user)
    return render(request, "assessment/student_results.html", {"results": qs})


@login_required
def batch_results(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id)
    results = Result.objects.filter(assessment=assessment).select_related("student")
    return render(request, "assessment/batch_results.html", {"assessment": assessment, "results": results})


@login_required
def generate_final_result(request, batch_id):
    batch = get_object_or_404(Assessment._meta.get_field("batch").remote_field.model, pk=batch_id)
    _require_teacher_or_admin(request.user)
    FinalResult.recompute_for_batch(batch)
    messages.success(request, "Final results generated.")
    return redirect("assessment:final_result_view", batch_id=batch.id)


@login_required
def final_result_view(request, batch_id=None):
    qs = FinalResult.objects.select_related("student", "batch")
    if batch_id:
        qs = qs.filter(batch_id=batch_id)
    if _is_student(request.user):
        qs = qs.filter(student=request.user)
    return render(request, "assessment/final_results.html", {"final_results": qs})
