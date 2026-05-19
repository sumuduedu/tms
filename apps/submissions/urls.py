from django.urls import path

from .views import GradeSubmissionView, SubmissionHistoryView, TeacherSubmissionListView, submit_exercise

app_name = "submissions"

urlpatterns = [
    path("history/", SubmissionHistoryView.as_view(), name="history"),
    path("teacher/", TeacherSubmissionListView.as_view(), name="teacher-list"),
    path("<int:pk>/grade/", GradeSubmissionView.as_view(), name="grade"),
    path("exercise/<int:pk>/submit/", submit_exercise, name="submit"),
]
