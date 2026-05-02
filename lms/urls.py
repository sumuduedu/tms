from django.urls import path

from . import views

app_name = "lms"

urlpatterns = [
    path("content/<int:batch_id>/", views.content_list, name="content_list"),
    path("content/create/<int:batch_id>/", views.content_create, name="content_create"),
    path("content/<int:id>/", views.content_detail, name="content_detail"),
    path("activities/<int:batch_id>/", views.activity_list, name="activity_list"),
    path("activities/create/<int:batch_id>/", views.activity_create, name="activity_create"),
    path("activities/<int:id>/", views.activity_detail, name="activity_detail"),
    path("submit/<int:activity_id>/", views.submit_activity, name="submit_activity"),
    path("submissions/<int:activity_id>/", views.submission_list, name="submission_list"),
    path("evaluate/<int:submission_id>/", views.evaluate_submission, name="evaluate_submission"),
]
