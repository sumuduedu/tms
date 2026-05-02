from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Batch(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        UPCOMING = "upcoming", "Upcoming"

    name = models.CharField(max_length=150)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="batches")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="teaching_batches",
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="student_batches",
        blank=True,
        through="BatchStudent",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING)

    class Meta:
        ordering = ["-start_date", "name"]
        unique_together = ("name", "course")

    def __str__(self):
        return f"{self.name} - {self.course}"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": "End date cannot be earlier than start date."})

        if self.teacher_id and getattr(self.teacher, "role", None) != "teacher":
            raise ValidationError({"teacher": "Assigned user must have teacher role."})


class BatchStudent(models.Model):
    """Through model for validation and future extensibility."""

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("batch", "student")

    def __str__(self):
        return f"{self.student} in {self.batch}"

    def clean(self):
        super().clean()
        if getattr(self.student, "role", None) != "student":
            raise ValidationError({"student": "Only users with student role can be assigned."})

        enrollment_exists = self.student.enrollments.filter(course=self.batch.course).exists()
        if not enrollment_exists:
            raise ValidationError("Student must be enrolled in this batch course before assignment.")
