from django.contrib import admin

from .models import StudentProfile, Submission, SubmissionAttachment, TeacherProfile

admin.site.register(Submission)
admin.site.register(SubmissionAttachment)
admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
