from django import forms
from django.core.exceptions import ValidationError

from .models import LessonPlan, Timetable


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ["date", "start_time", "end_time", "topic", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class LessonPlanForm(forms.ModelForm):
    class Meta:
        model = LessonPlan
        fields = [
            "timetable",
            "topic",
            "objectives",
            "activities",
            "resources",
            "assessment_method",
        ]

    def __init__(self, *args, **kwargs):
        self.batch = kwargs.pop("batch", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.batch is not None:
            self.fields["timetable"].queryset = Timetable.objects.filter(batch=self.batch)

    def clean(self):
        cleaned_data = super().clean()
        timetable = cleaned_data.get("timetable")

        if timetable and self.batch and timetable.batch_id != self.batch.id:
            raise ValidationError("Timetable must belong to the selected batch.")

        return cleaned_data
