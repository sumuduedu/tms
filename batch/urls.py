from django.urls import path

from . import views

urlpatterns = [
    path("batches/", views.batch_list, name="batch_list"),
    path("batches/create/", views.batch_create, name="batch_create"),
    path("batches/<int:pk>/", views.batch_detail, name="batch_detail"),
    path("batches/<int:pk>/edit/", views.batch_update, name="batch_update"),
    path("batches/<int:pk>/delete/", views.batch_delete, name="batch_delete"),
    path("batches/<int:pk>/assign-students/", views.assign_students_to_batch, name="assign_students_to_batch"),
    path("my-batches/", views.my_batches, name="my_batches"),
    path("my-batch/", views.student_batch_view, name="student_batch_view"),
]
