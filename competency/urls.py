from django.urls import path

from . import views

urlpatterns = [
    path("ncs/", views.ncsunit_list, name="ncsunit_list"),
    path("competencies/", views.competency_list, name="competency_list"),
    path("tasks/", views.task_list, name="task_list"),
    path("competency/assess/<int:student_id>/<int:competency_id>/", views.assess_competency, name="assess_competency"),
    path("competency/records/<int:batch_id>/", views.competency_records_by_batch, name="competency_records_by_batch"),
    path("my-competencies/", views.my_competencies, name="my_competencies"),
]
