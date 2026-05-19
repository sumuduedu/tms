from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class Exercise(models.Model):
    class Category(models.TextChoices):
        MS_WORD = "MS Word", "MS Word"
        MS_EXCEL = "MS Excel", "MS Excel"
        POWERPOINT = "PowerPoint", "PowerPoint"
        HTML = "HTML", "HTML"
        PYTHON = "Python", "Python"
        DATABASE = "Database", "Database"
        NETWORKING = "Networking", "Networking"
        GRAPHIC_DESIGN = "Graphic Design", "Graphic Design"

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exercises")
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=Category.choices)
    description = models.TextField()
    instruction_file = models.FileField(
        upload_to="instructions/",
        validators=[FileExtensionValidator(["pdf", "docx", "xlsx", "pptx", "zip", "jpg", "jpeg", "png", "html"])],
    )
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ExerciseResource(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="resources")
    file = models.FileField(
        upload_to="resources/",
        validators=[FileExtensionValidator(["pdf", "docx", "xlsx", "pptx", "zip", "jpg", "jpeg", "png", "html"])],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resource for {self.exercise.title}"
