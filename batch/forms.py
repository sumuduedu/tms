from django import forms
from django.contrib.auth import get_user_model

from .models import Batch

User = get_user_model()


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = [
            "name",
            "course",
            "teacher",
            "start_date",
            "end_date",
            "status",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = User.objects.filter(role="teacher")


class AssignStudentForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        batch = kwargs.pop("batch")
        super().__init__(*args, **kwargs)
        self.batch = batch
        self.fields["students"].queryset = User.objects.filter(
            role="student",
            enrollments__course=batch.course,
        ).distinct()
        self.fields["students"].initial = batch.students.values_list("id", flat=True)

    def save(self):
        selected_students = self.cleaned_data["students"]
        self.batch.students.set(selected_students)
        return self.batch
