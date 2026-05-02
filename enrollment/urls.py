from django.urls import path

from . import views

app_name = "enrollment"

urlpatterns = [
    path("apply/<int:course_id>/", views.apply_course, name="apply_course"),
    path("my/", views.my_requests, name="my_requests"),
    path("requests/", views.request_list, name="request_list"),
    path("approve/<int:id>/", views.approve_request, name="approve_request"),
    path("reject/<int:id>/", views.reject_request, name="reject_request"),
]
