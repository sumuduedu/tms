from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

from apps.exercises.models import Exercise


class Submission(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    submission_file = models.FileField(
        upload_to="submissions/",
        validators=[FileExtensionValidator(["pdf", "docx", "xlsx", "pptx", "zip", "jpg", "jpeg", "png", "html"])],
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ("exercise", "student")
        ordering = ["-submitted_at"]

    @property
    def review_status(self):
        return "Reviewed" if self.marks is not None else "Pending"


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    institute_id = models.CharField(max_length=50, unique=True)


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile")
    department = models.CharField(max_length=100)
