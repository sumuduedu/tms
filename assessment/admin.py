from django.contrib import admin

from .models import Assessment, Attendance, FinalResult, Result


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("batch", "student", "date", "status", "marked_by")
    list_filter = ("batch", "date", "status")
    search_fields = ("student__username", "batch__name")


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "batch", "assessment_type", "total_marks", "date", "created_by")
    list_filter = ("batch", "date", "assessment_type")
    search_fields = ("title", "batch__name")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("assessment", "student", "marks_obtained", "grade")
    list_filter = ("assessment__batch", "assessment__assessment_type")
    search_fields = ("student__username", "assessment__title")


@admin.register(FinalResult)
class FinalResultAdmin(admin.ModelAdmin):
    list_display = ("batch", "student", "total_marks", "average_marks", "status", "completed")
    list_filter = ("batch", "status", "completed")
    search_fields = ("student__username", "batch__name")
