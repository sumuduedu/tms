from django import forms

from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["submission_file"]


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["marks", "feedback"]
