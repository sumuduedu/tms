from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.exercises.models import Exercise
from apps.submissions.models import Submission


def home(request):
    return render(request, "dashboard/home.html")


@login_required
def dashboard(request):
    if request.user.role == "Teacher":
        data = {
            "exercise_count": Exercise.objects.filter(teacher=request.user).count(),
            "submission_count": Submission.objects.filter(exercise__teacher=request.user).count(),
        }
        return render(request, "dashboard/teacher_dashboard.html", data)
    data = {
        "exercise_count": Exercise.objects.count(),
        "submission_count": Submission.objects.filter(student=request.user).count(),
    }
    return render(request, "dashboard/student_dashboard.html", data)
