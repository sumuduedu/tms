from django.urls import path

from .views import HomeView, StudentDashboardView, TeacherDashboardView, TeacherStudentsView, dashboard

from .views import dashboard, home


app_name = "dashboard"

urlpatterns = [

    path("", HomeView.as_view(), name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("teacher/", TeacherDashboardView.as_view(), name="teacher"),
    path("teacher/students/", TeacherStudentsView.as_view(), name="teacher-students"),
    path("student/", StudentDashboardView.as_view(), name="student"),

    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),

]
