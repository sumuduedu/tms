
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Timetable(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", _("Scheduled")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    batch = models.ForeignKey(
        "batch_management.Batch",
        on_delete=models.CASCADE,
        related_name="timetable_entries",
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    topic = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    class Meta:
        ordering = ["date", "start_time"]
        indexes = [models.Index(fields=["batch", "date"])]

    def __str__(self):
        return f"{self.batch} | {self.date} {self.start_time}-{self.end_time} | {self.topic}"

    def clean(self):
        super().clean()

        if self.start_time >= self.end_time:
            raise ValidationError({"end_time": _("End time must be after start time.")})

        overlapping = Timetable.objects.filter(batch=self.batch, date=self.date).exclude(pk=self.pk)
        overlapping = overlapping.filter(start_time__lt=self.end_time, end_time__gt=self.start_time)

        if overlapping.exists():
            raise ValidationError(_("This session overlaps with another timetable entry for the same batch."))


class LessonPlan(models.Model):
    batch = models.ForeignKey(
        "batch_management.Batch",
        on_delete=models.CASCADE,
        related_name="lesson_plans",
    )
    timetable = models.OneToOneField(
        Timetable,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lesson_plan",
    )
    topic = models.CharField(max_length=255)
    objectives = models.TextField()
    activities = models.TextField()
    resources = models.TextField(blank=True)
    assessment_method = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lesson_plans_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["batch", "topic"], name="unique_lessonplan_topic_per_batch"),
        ]

    def __str__(self):
        return f"{self.batch} | {self.topic}"

    def clean(self):
        super().clean()

        if getattr(self.created_by, "role", None) != "teacher":
            raise ValidationError({"created_by": _("Only teachers can create lesson plans.")})

        assigned_teacher_id = getattr(self.batch, "teacher_id", None)
        if assigned_teacher_id is not None and self.created_by_id != assigned_teacher_id:
            raise ValidationError(_("Only the assigned teacher can create lesson plans for this batch."))

        if self.timetable and self.timetable.batch_id != self.batch_id:
            raise ValidationError({"timetable": _("Selected timetable does not belong to this batch.")})

        if self.timetable and self.topic and self.topic != self.timetable.topic:
            raise ValidationError({"topic": _("Lesson plan topic must match the linked timetable topic.")})
