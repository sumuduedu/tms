from django.urls import path

from .views import dashboard, home

app_name = "dashboard"

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
]
