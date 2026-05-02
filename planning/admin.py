from django.contrib import admin

from .models import LessonPlan, Timetable


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("batch", "date", "start_time", "end_time", "topic", "status")
    list_filter = ("batch", "date", "status")
    search_fields = ("topic", "batch__name")


@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ("batch", "topic", "created_by", "created_at")
    list_filter = ("batch", "created_at")
    search_fields = ("topic", "batch__name", "created_by__username")
