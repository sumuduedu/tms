from django.contrib import admin

from .models import Enrollment, EnrollmentRequest


@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "status", "created_at")
    list_filter = ("status", "course", "created_at")
    search_fields = ("student__username", "student__email", "course__title")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("course", "enrolled_at")
    search_fields = ("student__username", "student__email", "course__title")
