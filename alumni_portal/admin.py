from django.contrib import admin

from .models import AlumniProfile, JobPost


@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "batch", "completion_date", "company")
    search_fields = ("user__username", "user__email", "company", "skills")
    list_filter = ("course", "batch")


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ("title", "company_name", "location", "posted_by", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "company_name", "location", "posted_by__username")
