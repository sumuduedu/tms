from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

from apps.exercises.models import Exercise



ALLOWED_FILE_EXTENSIONS = ["pdf", "docx", "xlsx", "pptx", "zip", "jpg", "jpeg", "png", "html"]



class Submission(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    submission_file = models.FileField(
        upload_to="submissions/",

        validators=[FileExtensionValidator(ALLOWED_FILE_EXTENSIONS)],
        blank=True,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    marks = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="graded_submissions",
    )

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



class SubmissionAttachment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="submissions/", validators=[FileExtensionValidator(ALLOWED_FILE_EXTENSIONS)])
    uploaded_at = models.DateTimeField(auto_now_add=True)



class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    institute_id = models.CharField(max_length=50, unique=True)


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile")
    department = models.CharField(max_length=100)
