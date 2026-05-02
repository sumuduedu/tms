from django.urls import path

from . import views

app_name = "alumni"

urlpatterns = [
    path("alumni/", views.alumni_list, name="alumni_list"),
    path("alumni/profile/", views.my_profile, name="my_profile"),
    path("alumni/profile/edit/", views.update_profile, name="update_profile"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/create/", views.job_create, name="job_create"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/edit/", views.job_update, name="job_update"),
    path("jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
]
