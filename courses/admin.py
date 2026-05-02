from django.contrib import admin

from .models import Course, Module


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description")
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "order")
    list_filter = ("course",)
    search_fields = ("name", "description", "course__title")
    ordering = ("course", "order")
