from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.exercises.models import Exercise
from apps.submissions.models import StudentProfile, TeacherProfile


class Command(BaseCommand):
    help = "Seed demo data for ICT Exercise Management System"

    def handle(self, *args, **options):
        teacher, _ = User.objects.get_or_create(email="teacher@example.com", defaults={"role": "Teacher", "first_name": "Demo"})
        teacher.set_password("Pass@12345")
        teacher.save()
        TeacherProfile.objects.get_or_create(user=teacher, defaults={"department": "ICT"})

        student, _ = User.objects.get_or_create(email="student@example.com", defaults={"role": "Student", "first_name": "Demo"})
        student.set_password("Pass@12345")
        student.save()
        StudentProfile.objects.get_or_create(user=student, defaults={"institute_id": "STD001"})

        Exercise.objects.get_or_create(
            teacher=teacher,
            title="Basic HTML Portfolio",
            defaults={
                "category": "HTML",
                "description": "Create a portfolio page using semantic HTML.",
                "instruction_file": "instructions/sample.pdf",
                "deadline": timezone.now() + timezone.timedelta(days=7),
            },
        )
        self.stdout.write(self.style.SUCCESS("Seed data created. teacher@example.com / student@example.com"))
