from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import Certificate


def _require_staff_or_teacher(user):
    return user.is_superuser or user.is_staff or getattr(user, "role", "").lower() == "teacher"


def _require_admin_or_staff(user):
    return user.is_superuser or user.is_staff


@login_required
def generate_certificate(request, student_id, batch_id):
    if not _require_admin_or_staff(request.user):
        raise PermissionDenied

    if not Certificate.is_eligible_for_issue(student_id, batch_id):
        messages.error(request, "Student is not eligible for certificate issuance.")
        return redirect("certificate_list")

    certificate, created = Certificate.objects.get_or_create(
        student_id=student_id,
        batch_id=batch_id,
        defaults={
            "certificate_id": Certificate.generate_certificate_id(),
            "issue_date": timezone.localdate(),
            "status": Certificate.STATUS_ISSUED,
        },
    )

    if not created and certificate.status != Certificate.STATUS_ISSUED:
        certificate.status = Certificate.STATUS_ISSUED
        certificate.issue_date = timezone.localdate()
        certificate.save(update_fields=["status", "issue_date", "updated_at"])

    messages.success(request, f"Certificate {certificate.certificate_id} is ready.")
    return redirect("certificate_list")


@login_required
def certificate_list(request):
    if not _require_staff_or_teacher(request.user):
        raise PermissionDenied

    certificates = Certificate.objects.select_related("student", "batch")
    return render(request, "certification/certificate_list.html", {"certificates": certificates})


@login_required
def my_certificates(request):
    certificates = Certificate.objects.filter(student=request.user).select_related("batch")
    return render(request, "certification/my_certificates.html", {"certificates": certificates})


def _build_certificate_pdf(certificate: Certificate):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as exc:
        raise Http404("PDF generation library is unavailable.") from exc

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 26)
    p.drawCentredString(width / 2, height - 120, "Course Completion Certificate")

    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2, height - 180, "This certifies that")
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 220, certificate.student.get_full_name() or certificate.student.username)

    p.setFont("Helvetica", 14)
    p.drawCentredString(width / 2, height - 260, "has successfully completed")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 290, str(certificate.batch.course))

    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, height - 320, f"Batch: {certificate.batch}")
    p.drawCentredString(width / 2, height - 340, f"Issue Date: {certificate.issue_date:%B %d, %Y}")
    p.drawCentredString(width / 2, height - 360, f"Certificate ID: {certificate.certificate_id}")

    p.line(width - 220, 120, width - 80, 120)
    p.drawString(width - 190, 100, "Authorized Signature")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


@login_required
def download_certificate(request, id):
    certificate = get_object_or_404(Certificate.objects.select_related("student", "batch", "batch__course"), id=id)

    if not (_require_staff_or_teacher(request.user) or certificate.student_id == request.user.id):
        raise PermissionDenied

    if certificate.file:
        return FileResponse(certificate.file.open("rb"), as_attachment=True, filename=f"{certificate.certificate_id}.pdf")

    buffer = _build_certificate_pdf(certificate)
    return FileResponse(buffer, as_attachment=True, filename=f"{certificate.certificate_id}.pdf")
