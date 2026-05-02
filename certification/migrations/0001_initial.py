from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("training", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Certificate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("certificate_id", models.CharField(max_length=32, unique=True)),
                ("issue_date", models.DateField(default=django.utils.timezone.localdate)),
                ("file", models.FileField(blank=True, null=True, upload_to="certificates/")),
                ("status", models.CharField(choices=[("Issued", "Issued"), ("Pending", "Pending")], default="Pending", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="certificates", to="training.batch")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="certificates", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-issue_date", "-id"]},
        ),
        migrations.AddConstraint(
            model_name="certificate",
            constraint=models.UniqueConstraint(fields=("student", "batch"), name="unique_certificate_per_student_batch"),
        ),
    ]
