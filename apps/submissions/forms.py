from django import forms

from .models import Submission


class SubmissionForm(forms.ModelForm):
    extra_files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
        help_text="You can upload multiple files.",
    )

    class Meta:
        model = Submission
        fields = ["submission_file", "extra_files"]


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["marks", "feedback"]
