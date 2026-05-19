from django.urls import path

from .views import (
    ExerciseCreateView,
    ExerciseDeleteView,
    ExerciseDetailView,
    ExerciseListView,
    ExerciseUpdateView,
    ManageExerciseListView,
)

app_name = "exercises"

urlpatterns = [
    path("", ExerciseListView.as_view(), name="list"),
    path("<int:pk>/", ExerciseDetailView.as_view(), name="detail"),
    path("manage/", ManageExerciseListView.as_view(), name="manage"),
    path("create/", ExerciseCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", ExerciseUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", ExerciseDeleteView.as_view(), name="delete"),
]
