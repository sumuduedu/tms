from django import forms

from .models import EnrollmentRequest


class EnrollmentRequestForm(forms.ModelForm):
    class Meta:
        model = EnrollmentRequest
        fields = ["course", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional message"}),
        }
