from django.urls import path

from .views import (
    LessonPlanCreateView,
    LessonPlanDetailView,
    LessonPlanListView,
    TimetableCreateView,
    TimetableDeleteView,
    TimetableListView,
    TimetableUpdateView,
)

app_name = "planning"

urlpatterns = [
    path("timetable/<int:batch_id>/", TimetableListView.as_view(), name="timetable_list"),
    path("timetable/create/<int:batch_id>/", TimetableCreateView.as_view(), name="timetable_create"),
    path("timetable/<int:pk>/edit/", TimetableUpdateView.as_view(), name="timetable_update"),
    path("timetable/<int:pk>/delete/", TimetableDeleteView.as_view(), name="timetable_delete"),
    path("lesson-plans/<int:batch_id>/", LessonPlanListView.as_view(), name="lessonplan_list"),
    path("lesson-plans/create/<int:batch_id>/", LessonPlanCreateView.as_view(), name="lessonplan_create"),
    path("lesson-plans/<int:pk>/", LessonPlanDetailView.as_view(), name="lessonplan_detail"),
]
