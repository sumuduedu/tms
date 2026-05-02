from django import forms

from .models import Competency, CompetencyRecord, NCSUnit, Task


class NCSUnitForm(forms.ModelForm):
    class Meta:
        model = NCSUnit
        fields = ["code", "title", "description", "module"]


class CompetencyForm(forms.ModelForm):
    class Meta:
        model = Competency
        fields = ["unit", "name", "description"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["competency", "title", "description"]


class CompetencyRecordForm(forms.ModelForm):
    class Meta:
        model = CompetencyRecord
        fields = ["status", "remarks"]
