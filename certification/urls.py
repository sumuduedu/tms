from django.urls import path

from . import views

urlpatterns = [
    path("", views.certificate_list, name="certificate_list"),
    path("generate/<int:student_id>/<int:batch_id>/", views.generate_certificate, name="generate_certificate"),
    path("my/", views.my_certificates, name="my_certificates"),
    path("download/<int:id>/", views.download_certificate, name="download_certificate"),
]
