from django.contrib import admin

from .models import Batch, BatchStudent


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "teacher", "status", "start_date", "end_date")
    list_filter = ("status", "course")
    search_fields = ("name", "course__title", "teacher__email")
    filter_horizontal = ("students",)


@admin.register(BatchStudent)
class BatchStudentAdmin(admin.ModelAdmin):
    list_display = ("batch", "student", "assigned_at")
    search_fields = ("batch__name", "student__email")
