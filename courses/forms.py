from django import forms

from .models import Course, Module


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "duration", "fee", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["name", "description", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
