from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps


class AlumniProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alumni_profile",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="alumni_profiles",
    )
    batch = models.ForeignKey(
        "courses.Batch",
        on_delete=models.PROTECT,
        related_name="alumni_profiles",
    )
    completion_date = models.DateField()
    current_job = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    skills = models.TextField()
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-completion_date", "user__username"]

    def __str__(self):
        return f"{self.user} - {self.course}"


class JobPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_posts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company_name}"

    def clean(self):
        role = getattr(self.posted_by, "role", None)
        is_alumni = hasattr(self.posted_by, "alumni_profile")
        is_admin = bool(getattr(self.posted_by, "is_staff", False) or getattr(self.posted_by, "is_superuser", False))
        if role not in {"alumni", "admin", "staff"} and not (is_alumni or is_admin):
            raise ValidationError("Only alumni or admin/staff users can post jobs.")


@receiver(post_save, sender="results.FinalResult")
def create_alumni_profile_on_pass(sender, instance, created, **kwargs):
    """
    Create AlumniProfile when FinalResult is marked Pass and certificate exists.
    Expects FinalResult to have student/user, course, batch, status, completion_date fields.
    """
    status = str(getattr(instance, "status", "")).lower()
    if status != "pass":
        return

    user = getattr(instance, "student", None) or getattr(instance, "user", None)
    course = getattr(instance, "course", None)
    batch = getattr(instance, "batch", None)
    completion_date = getattr(instance, "completion_date", None)

    if not user or not course or not batch or not completion_date:
        return

    Certificate = apps.get_model("certificates", "Certificate")
    cert_exists = Certificate.objects.filter(user=user, course=course).exists()
    if not cert_exists:
        return

    AlumniProfile.objects.get_or_create(
        user=user,
        defaults={
            "course": course,
            "batch": batch,
            "completion_date": completion_date,
            "skills": "",
        },
    )

    if getattr(user, "role", "") == "student":
        user.role = "alumni"
        user.save(update_fields=["role"])
