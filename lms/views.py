from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ActivityForm, EvaluationForm, SubmissionForm, ContentForm
from .models import Activity, ActivitySubmission, Content


def _is_teacher(user):
    return user.is_staff or getattr(user, "role", None) == "teacher"


def _is_student(user):
    return user.is_staff or getattr(user, "role", None) == "student"


def _teacher_for_batch(user, batch):
    return user.is_staff or batch.teachers.filter(id=user.id).exists()


def _student_in_batch(user, batch):
    return user.is_staff or batch.students.filter(id=user.id).exists()


@login_required
def content_list(request, batch_id):
    batch = get_object_or_404(Activity._meta.get_field("batch").remote_field.model, id=batch_id)
    if not (_teacher_for_batch(request.user, batch) or _student_in_batch(request.user, batch)):
        raise PermissionDenied
    contents = Content.objects.filter(batch=batch).select_related("lesson_plan", "uploaded_by")
    return render(request, "lms/content_list.html", {"batch": batch, "contents": contents})


@login_required
def content_create(request, batch_id):
    batch = get_object_or_404(Activity._meta.get_field("batch").remote_field.model, id=batch_id)
    if not (_is_teacher(request.user) and _teacher_for_batch(request.user, batch)):
        raise PermissionDenied
    form = ContentForm(request.POST or None, request.FILES or None)
    form.fields["lesson_plan"].queryset = batch.lesson_plans.all()
    if form.is_valid():
        content = form.save(commit=False)
        content.batch = batch
        content.uploaded_by = request.user
        content.save()
        messages.success(request, "Content uploaded successfully.")
        return redirect("lms:content_detail", id=content.id)
    return render(request, "lms/content_form.html", {"form": form, "batch": batch})


@login_required
def content_detail(request, id):
    content = get_object_or_404(Content.objects.select_related("batch", "lesson_plan", "uploaded_by"), id=id)
    if not (_teacher_for_batch(request.user, content.batch) or _student_in_batch(request.user, content.batch)):
        raise PermissionDenied
    return render(request, "lms/content_detail.html", {"content": content})


@login_required
def activity_list(request, batch_id):
    batch = get_object_or_404(Activity._meta.get_field("batch").remote_field.model, id=batch_id)
    if not (_teacher_for_batch(request.user, batch) or _student_in_batch(request.user, batch)):
        raise PermissionDenied
    activities = Activity.objects.filter(batch=batch).select_related("created_by")
    return render(request, "lms/activity_list.html", {"batch": batch, "activities": activities})


@login_required
def activity_create(request, batch_id):
    batch = get_object_or_404(Activity._meta.get_field("batch").remote_field.model, id=batch_id)
    if not (_is_teacher(request.user) and _teacher_for_batch(request.user, batch)):
        raise PermissionDenied
    form = ActivityForm(request.POST or None)
    if form.is_valid():
        activity = form.save(commit=False)
        activity.batch = batch
        activity.created_by = request.user
        activity.save()
        messages.success(request, "Activity created successfully.")
        return redirect("lms:activity_detail", id=activity.id)
    return render(request, "lms/activity_form.html", {"form": form, "batch": batch})


@login_required
def activity_detail(request, id):
    activity = get_object_or_404(Activity.objects.select_related("batch", "created_by"), id=id)
    if not (_teacher_for_batch(request.user, activity.batch) or _student_in_batch(request.user, activity.batch)):
        raise PermissionDenied
    submission = None
    if _is_student(request.user):
        submission = ActivitySubmission.objects.filter(activity=activity, student=request.user).first()
    return render(request, "lms/activity_detail.html", {"activity": activity, "submission": submission})


@login_required
def submit_activity(request, activity_id):
    activity = get_object_or_404(Activity.objects.select_related("batch"), id=activity_id)
    if not (_is_student(request.user) and _student_in_batch(request.user, activity.batch)):
        raise PermissionDenied
    submission = ActivitySubmission.objects.filter(activity=activity, student=request.user).first()
    if submission:
        messages.info(request, "You have already submitted this activity.")
        return redirect("lms:activity_detail", id=activity.id)

    form = SubmissionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.activity = activity
        obj.student = request.user
        obj.save()
        messages.success(request, "Submission uploaded successfully.")
        return redirect("lms:activity_detail", id=activity.id)
    return render(request, "lms/submission_form.html", {"form": form, "activity": activity})


@login_required
def submission_list(request, activity_id):
    activity = get_object_or_404(Activity.objects.select_related("batch"), id=activity_id)
    if not (_is_teacher(request.user) and _teacher_for_batch(request.user, activity.batch)):
        raise PermissionDenied
    submissions = activity.submissions.select_related("student")
    return render(request, "lms/submission_list.html", {"activity": activity, "submissions": submissions})


@login_required
def evaluate_submission(request, submission_id):
    submission = get_object_or_404(ActivitySubmission.objects.select_related("activity__batch"), id=submission_id)
    if not (_is_teacher(request.user) and _teacher_for_batch(request.user, submission.activity.batch)):
        raise PermissionDenied
    form = EvaluationForm(request.POST or None, instance=submission)
    if form.is_valid():
        form.save()
        messages.success(request, "Submission evaluated successfully.")
        return redirect("lms:submission_list", activity_id=submission.activity_id)
    return render(request, "lms/evaluation_form.html", {"form": form, "submission": submission})
