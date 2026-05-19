from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView

from apps.exercises.models import Exercise

from .forms import GradeSubmissionForm, SubmissionForm
from .models import Submission


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
        return Submission.objects.filter(student=self.request.user)


class TeacherSubmissionListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Submission
    template_name = "submissions/teacher_submissions.html"

    def get_queryset(self):
        return Submission.objects.filter(exercise__teacher=self.request.user).select_related("exercise", "student")


class GradeSubmissionView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Submission
    form_class = GradeSubmissionForm
    template_name = "submissions/grade_submission.html"
    success_url = reverse_lazy("submissions:teacher-list")

    def get_queryset(self):
        return Submission.objects.filter(exercise__teacher=self.request.user)


def submit_exercise(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.user.role != "Student":
        return redirect("dashboard:home")
    submission, _ = Submission.objects.get_or_create(exercise=exercise, student=request.user)
    form = SubmissionForm(request.POST or None, request.FILES or None, instance=submission)
    if request.method == "POST" and form.is_valid():
        form.instance.exercise = exercise
        form.instance.student = request.user
        form.save()
        messages.success(request, "Submission uploaded successfully.")
        return redirect("submissions:history")
    return render(request, "submissions/submit_exercise.html", {"form": form, "exercise": exercise})
