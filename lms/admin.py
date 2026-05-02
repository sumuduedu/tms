from django.contrib import admin

from .models import Activity, ActivitySubmission, Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "batch", "content_type", "uploaded_by", "created_at")
    list_filter = ("batch", "content_type", "created_at")
    search_fields = ("title", "description", "uploaded_by__username")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "batch", "activity_type", "due_date", "created_by", "created_at")
    list_filter = ("batch", "activity_type", "due_date")
    search_fields = ("title", "description", "created_by__username")


@admin.register(ActivitySubmission)
class ActivitySubmissionAdmin(admin.ModelAdmin):
    list_display = ("activity", "student", "submitted_at", "marks")
    list_filter = ("activity__batch", "activity__activity_type", "submitted_at")
    search_fields = ("activity__title", "student__username", "feedback")
