from django.contrib import admin

from .models import Competency, CompetencyRecord, NCSUnit, Task


@admin.register(NCSUnit)
class NCSUnitAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "module")
    search_fields = ("code", "title")
    list_filter = ("module",)


@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    list_display = ("name", "unit")
    search_fields = ("name", "unit__code", "unit__title")
    list_filter = ("unit",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "competency", "get_unit")
    search_fields = ("title", "competency__name", "competency__unit__code")
    list_filter = ("competency__unit",)

    @admin.display(description="Unit")
    def get_unit(self, obj):
        return obj.competency.unit


@admin.register(CompetencyRecord)
class CompetencyRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "competency", "status", "assessed_by", "assessed_at")
    search_fields = ("student__username", "competency__name", "competency__unit__code")
    list_filter = ("status", "competency__unit")
