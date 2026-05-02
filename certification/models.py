from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Certificate(models.Model):
    STATUS_ISSUED = "Issued"
    STATUS_PENDING = "Pending"
    STATUS_CHOICES = (
        (STATUS_ISSUED, "Issued"),
        (STATUS_PENDING, "Pending"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    batch = models.ForeignKey(
        "training.Batch",
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    certificate_id = models.CharField(max_length=32, unique=True)
    issue_date = models.DateField(default=timezone.localdate)
    file = models.FileField(upload_to="certificates/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "batch"], name="unique_certificate_per_student_batch"),
        ]
        ordering = ["-issue_date", "-id"]

    def __str__(self) -> str:
        return f"{self.certificate_id} - {self.student}"

    def clean(self):
        super().clean()
        if self.status == self.STATUS_ISSUED:
            if not self.is_eligible_for_issue(self.student_id, self.batch_id):
                raise ValidationError("Certificate can only be issued for a completed and passed final result.")

    @staticmethod
    def is_eligible_for_issue(student_id: int, batch_id: int) -> bool:
        if not student_id or not batch_id:
            return False
        from results.models import FinalResult

        return FinalResult.objects.filter(
            student_id=student_id,
            batch_id=batch_id,
            status="Pass",
            completed=True,
        ).exists()

    @classmethod
    def generate_certificate_id(cls) -> str:
        year = timezone.now().year
        prefix = f"CERT-{year}-"
        latest = (
            cls.objects.filter(certificate_id__startswith=prefix)
            .order_by("-certificate_id")
            .values_list("certificate_id", flat=True)
            .first()
        )
        if latest:
            serial = int(latest.split("-")[-1]) + 1
        else:
            serial = 1
        return f"{prefix}{serial:04d}"
