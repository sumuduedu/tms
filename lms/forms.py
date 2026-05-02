from django import forms

from .models import Activity, ActivitySubmission, Content


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ["lesson_plan", "title", "description", "content_type", "file", "url", "text_content"]


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["title", "description", "activity_type", "due_date"]
        widgets = {"due_date": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = ActivitySubmission
        fields = ["submission_text", "submission_file"]


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = ActivitySubmission
        fields = ["marks", "feedback"]
