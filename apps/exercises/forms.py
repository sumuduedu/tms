from django import forms
from django.forms import inlineformset_factory

from .models import Exercise, ExerciseResource


class ExerciseForm(forms.ModelForm):
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}))

    class Meta:
        model = Exercise
        fields = ["title", "category", "description", "instruction_file", "deadline"]


ExerciseResourceFormSet = inlineformset_factory(
    Exercise,
    ExerciseResource,
    fields=["file"],
    extra=3,
    can_delete=True,
)
