from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class NCSUnit(models.Model):
    code = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Optional mapping to Phase 2 module model.
    module = models.ForeignKey(
        "courses.Module",
        on_delete=models.SET_NULL,
        related_name="ncs_units",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.title}"


class Competency(models.Model):
    unit = models.ForeignKey(NCSUnit, on_delete=models.CASCADE, related_name="competencies")
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ["unit__code", "name"]
        unique_together = ("unit", "name")

    def __str__(self) -> str:
        return f"{self.unit.code}: {self.name}"


class Task(models.Model):
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ["competency__unit__code", "competency__name", "title"]
        unique_together = ("competency", "title")

    def __str__(self) -> str:
        return self.title


class CompetencyRecord(models.Model):
    STATUS_NOT_ACHIEVED = "not_achieved"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_ACHIEVED = "achieved"

    STATUS_CHOICES = (
        (STATUS_NOT_ACHIEVED, "Not Achieved"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_ACHIEVED, "Achieved"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="competency_records",
    )
    competency = models.ForeignKey(
        Competency,
        on_delete=models.CASCADE,
        related_name="records",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_ACHIEVED)
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assessed_competencies",
    )
    assessed_at = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["student", "competency__unit__code", "competency__name"]
        unique_together = ("student", "competency")

    def clean(self):
        super().clean()

        if hasattr(self.assessed_by, "role") and self.assessed_by.role != "teacher":
            raise ValidationError({"assessed_by": "Only teachers can assess competencies."})

        prior = None
        if self.pk:
            prior = CompetencyRecord.objects.filter(pk=self.pk).values_list("status", flat=True).first()

        allowed_transitions = {
            self.STATUS_NOT_ACHIEVED: {self.STATUS_NOT_ACHIEVED, self.STATUS_IN_PROGRESS},
            self.STATUS_IN_PROGRESS: {self.STATUS_IN_PROGRESS, self.STATUS_ACHIEVED},
            self.STATUS_ACHIEVED: {self.STATUS_ACHIEVED},
        }
        if prior and self.status not in allowed_transitions[prior]:
            raise ValidationError({"status": f"Invalid transition from '{prior}' to '{self.status}'."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student} - {self.competency} ({self.get_status_display()})"
