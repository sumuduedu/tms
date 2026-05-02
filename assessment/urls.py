from django.urls import path

from . import views

app_name = "assessment"

urlpatterns = [
    path("assessment/<int:batch_id>/", views.assessment_list, name="assessment_list"),
    path("assessment/create/<int:batch_id>/", views.assessment_create, name="assessment_create"),
    path("assessment/<int:id>/detail/", views.assessment_detail, name="assessment_detail"),
    path("attendance/<int:batch_id>/", views.attendance_list, name="attendance_list"),
    path("attendance/mark/<int:batch_id>/", views.mark_attendance, name="mark_attendance"),
    path("results/<int:assessment_id>/", views.enter_marks, name="enter_marks"),
    path("results/student/", views.student_results, name="student_results"),
    path("results/batch/<int:assessment_id>/", views.batch_results, name="batch_results"),
    path("final-result/<int:batch_id>/", views.generate_final_result, name="generate_final_result"),
    path("final-result/student/", views.final_result_view, name="final_result_student"),
    path("final-result/view/<int:batch_id>/", views.final_result_view, name="final_result_view"),
]
