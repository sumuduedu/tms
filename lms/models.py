from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Content(models.Model):
    class ContentType(models.TextChoices):
        FILE = "file", "File"
        VIDEO = "video", "Video"
        LINK = "link", "Link"
        TEXT = "text", "Text"

    batch = models.ForeignKey("academics.Batch", on_delete=models.CASCADE, related_name="contents")
    lesson_plan = models.ForeignKey(
        "academics.LessonPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contents",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=10, choices=ContentType.choices)
    file = models.FileField(upload_to="lms/content/files/", blank=True, null=True)
    url = models.URLField(blank=True)
    text_content = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_contents",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def clean(self):
        super().clean()
        if self.lesson_plan and self.lesson_plan.batch_id != self.batch_id:
            raise ValidationError("Selected lesson plan does not belong to this batch.")

        if self.content_type == self.ContentType.FILE and not self.file:
            raise ValidationError({"file": "File is required for file content."})
        if self.content_type in {self.ContentType.VIDEO, self.ContentType.LINK} and not self.url:
            raise ValidationError({"url": "URL is required for link/video content."})
        if self.content_type == self.ContentType.TEXT and not self.text_content:
            raise ValidationError({"text_content": "Text content is required."})

    def __str__(self):
        return f"{self.title} ({self.batch})"


class Activity(models.Model):
    class ActivityType(models.TextChoices):
        ASSIGNMENT = "assignment", "Assignment"
        QUIZ = "quiz", "Quiz"
        PRACTICE = "practice", "Practice"

    batch = models.ForeignKey("academics.Batch", on_delete=models.CASCADE, related_name="activities")
    title = models.CharField(max_length=255)
    description = models.TextField()
    activity_type = models.CharField(max_length=15, choices=ActivityType.choices)
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_activities"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("due_date", "-created_at")

    def __str__(self):
        return f"{self.title} - {self.batch}"


class ActivitySubmission(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_submissions"
    )
    submission_text = models.TextField(blank=True)
    submission_file = models.FileField(upload_to="lms/submissions/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ("-submitted_at",)
        constraints = [
            models.UniqueConstraint(fields=("activity", "student"), name="unique_activity_submission")
        ]

    def clean(self):
        super().clean()
        if not self.submission_text and not self.submission_file:
            raise ValidationError("Please provide submission text or upload a file.")
        if self.activity_id and timezone.now() > self.activity.due_date:
            raise ValidationError("Submission deadline has passed.")

    def __str__(self):
        return f"{self.activity} - {self.student}"
