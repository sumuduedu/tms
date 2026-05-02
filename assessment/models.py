from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg, Sum
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Attendance(TimeStampedModel):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"

    batch = models.ForeignKey("batch.Batch", on_delete=models.CASCADE, related_name="attendance_records")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=Status.choices)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance_records",
    )

    class Meta:
        ordering = ["-date", "student_id"]
        unique_together = ("batch", "student", "date")

    def clean(self):
        if self.batch_id and self.student_id and hasattr(self.batch, "students"):
            if not self.batch.students.filter(pk=self.student_id).exists():
                raise ValidationError("Student is not enrolled in this batch.")

    def __str__(self):
        return f"{self.batch_id} - {self.student_id} - {self.date}"


class Assessment(TimeStampedModel):
    class AssessmentType(models.TextChoices):
        QUIZ = "quiz", "Quiz"
        ASSIGNMENT = "assignment", "Assignment"
        PRACTICAL = "practical", "Practical"
        FINAL_EXAM = "final_exam", "Final Exam"

    batch = models.ForeignKey("batch.Batch", on_delete=models.CASCADE, related_name="assessments")
    title = models.CharField(max_length=255)
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    total_marks = models.PositiveIntegerField()
    date = models.DateField(default=timezone.localdate)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_assessments")

    class Meta:
        ordering = ["-date", "title"]

    def __str__(self):
        return f"{self.title} ({self.batch_id})"


class Result(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="results")
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="results")
    marks_obtained = models.PositiveIntegerField()
    grade = models.CharField(max_length=5, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ["assessment_id", "student_id"]
        unique_together = ("student", "assessment")

    def clean(self):
        if self.assessment_id and self.marks_obtained > self.assessment.total_marks:
            raise ValidationError({"marks_obtained": "Marks cannot exceed total marks."})

    def __str__(self):
        return f"{self.student_id} - {self.assessment_id}"


class FinalResult(TimeStampedModel):
    class FinalStatus(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="final_results")
    batch = models.ForeignKey("batch.Batch", on_delete=models.CASCADE, related_name="final_results")
    total_marks = models.FloatField(default=0)
    average_marks = models.FloatField(default=0)
    status = models.CharField(max_length=10, choices=FinalStatus.choices)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "batch")
        ordering = ["batch_id", "student_id"]

    @classmethod
    def recompute_for_batch(cls, batch, pass_threshold=40):
        assessments = Assessment.objects.filter(batch=batch)
        for student in batch.students.all():
            aggregate = Result.objects.filter(
                student=student,
                assessment__in=assessments,
            ).aggregate(total=Sum("marks_obtained"), avg=Avg("marks_obtained"))
            total = float(aggregate["total"] or 0)
            avg = float(aggregate["avg"] or 0)
            completed = assessments.exists() and assessments.count() == Result.objects.filter(
                student=student,
                assessment__in=assessments,
            ).count()
            status = cls.FinalStatus.PASS if avg >= pass_threshold else cls.FinalStatus.FAIL
            cls.objects.update_or_create(
                student=student,
                batch=batch,
                defaults={
                    "total_marks": total,
                    "average_marks": avg,
                    "status": status,
                    "completed": completed,
                },
            )

    def __str__(self):
        return f"{self.student_id} - {self.batch_id}"
