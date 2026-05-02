from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "student", "batch", "issue_date", "status")
    list_filter = ("status", "issue_date")
    search_fields = ("certificate_id", "student__username", "student__email", "batch__name")
    readonly_fields = ("certificate_id", "issue_date", "created_at", "updated_at")
