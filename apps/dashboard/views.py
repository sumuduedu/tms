from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count, Q
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import ListView, TemplateView

from apps.exercises.models import Exercise
from apps.submissions.models import Submission


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "Teacher"


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "Student"


class HomeView(TemplateView):
    template_name = "dashboard/home.html"


class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    template_name = "teacher/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        exercises = Exercise.objects.filter(teacher=user)
        submissions = Submission.objects.filter(exercise__teacher=user).select_related("student", "exercise")

        context.update(
            {
                "total_exercises": exercises.count(),
                "total_students": submissions.values("student").distinct().count(),
                "total_submissions": submissions.count(),
                "pending_reviews": submissions.filter(Q(marks__isnull=True) | Q(feedback="")).count(),
                "recent_uploads": submissions.order_by("-submitted_at")[:5],
                "latest_submissions": submissions.order_by("-submitted_at")[:8],
                "exercise_rows": exercises.annotate(total_submissions=Count("submissions")).order_by("-created_at")[:10],
                "deadline_warnings": exercises.filter(deadline__gte=timezone.now(), deadline__lte=timezone.now() + timezone.timedelta(days=2)).order_by("deadline")[:5],
            }
        )
        return context


class StudentDashboardView(StudentRequiredMixin, TemplateView):
    template_name = "student/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        exercises = Exercise.objects.all()
        submissions = Submission.objects.filter(student=user).select_related("exercise")
        completed_ids = set(submissions.values_list("exercise_id", flat=True))
        recent_feedback = submissions.exclude(feedback="").order_by("-submitted_at")[:5]

        context.update(
            {
                "total_exercises": exercises.count(),
                "completed_exercises": len(completed_ids),
                "pending_exercises": max(exercises.count() - len(completed_ids), 0),
                "average_marks": submissions.exclude(marks__isnull=True).aggregate(avg=Avg("marks"))["avg"],
                "recent_feedback": recent_feedback,
                "exercise_cards": exercises.order_by("deadline")[:12],
                "submission_history": submissions.order_by("-submitted_at")[:10],
            }
        )
        return context


class TeacherStudentsView(TeacherRequiredMixin, ListView):
    template_name = "teacher/students.html"
    context_object_name = "students"

    def get_queryset(self):
        return (
            Submission.objects.filter(exercise__teacher=self.request.user)
            .values("student__id", "student__first_name", "student__last_name", "student__email")
            .annotate(total_submissions=Count("id"), reviewed=Count("id", filter=Q(marks__isnull=False)))
            .order_by("student__email")
        )


def dashboard(request):
    if not request.user.is_authenticated:
        return render(request, "dashboard/home.html")
    if request.user.role == "Teacher":
        return TeacherDashboardView.as_view()(request)
    return StudentDashboardView.as_view()(request)
