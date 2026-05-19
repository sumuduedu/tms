from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, UpdateView

from apps.exercises.models import Exercise

from .forms import GradeSubmissionForm, SubmissionForm
from .models import Submission, SubmissionAttachment


class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "Teacher"


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "Student"


class SubmissionHistoryView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = Submission
    template_name = "submissions/submission_history.html"

    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user).select_related("exercise", "graded_by").prefetch_related("attachments")


class TeacherSubmissionListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Submission
    template_name = "submissions/teacher_submissions.html"

    def get_queryset(self):
        return Submission.objects.filter(exercise__teacher=self.request.user).select_related("exercise", "student", "graded_by").prefetch_related("attachments")


class GradeSubmissionView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Submission
    form_class = GradeSubmissionForm
    template_name = "submissions/grade_submission.html"
    success_url = reverse_lazy("submissions:teacher-list")

    def get_queryset(self):
        return Submission.objects.filter(exercise__teacher=self.request.user)

    def form_valid(self, form):
        submission = form.save(commit=False)
        submission.graded_by = self.request.user
        submission.graded_at = timezone.now()
        submission.save()
        messages.success(self.request, "Marks and feedback saved.")
        return redirect(self.success_url)


@login_required
def submit_exercise(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.user.role != "Student":
        return redirect("dashboard:home")

    submission = Submission.objects.filter(exercise=exercise, student=request.user).first()
    if submission and timezone.now() > exercise.deadline:
        messages.error(request, "Deadline passed. You cannot replace this submission.")
        return redirect("submissions:history")

    form = SubmissionForm(request.POST or None, request.FILES or None, instance=submission)
    if request.method == "POST" and form.is_valid():
        instance = form.save(commit=False)
        instance.exercise = exercise
        instance.student = request.user
        instance.save()

        if submission:
            submission.attachments.all().delete()
        for extra_file in request.FILES.getlist("extra_files"):
            SubmissionAttachment.objects.create(submission=instance, file=extra_file)

        messages.success(request, "Submission uploaded successfully.")
        return redirect("submissions:history")
    return render(request, "submissions/submit_exercise.html", {"form": form, "exercise": exercise, "submission": submission})
