from django import forms

from .models import AlumniProfile, JobPost


class AlumniProfileForm(forms.ModelForm):
    class Meta:
        model = AlumniProfile
        fields = ["skills", "current_job", "company", "bio"]
        widgets = {
            "skills": forms.Textarea(attrs={"rows": 4}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ["title", "description", "company_name", "location", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}
