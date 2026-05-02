from django import forms

from .models import Assessment, Attendance, Result


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["student", "date", "status"]


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ["title", "assessment_type", "total_marks", "date"]


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ["student", "marks_obtained", "grade", "feedback"]
