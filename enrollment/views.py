from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course

from .forms import EnrollmentRequestForm
from .models import Enrollment, EnrollmentRequest


def _is_student_or_parent(user):
    return user.is_authenticated and getattr(user, "role", None) in {"student", "parent"}


def _is_staff_or_admin(user):
    role = getattr(user, "role", None)
    return user.is_authenticated and (user.is_staff or user.is_superuser or role in {"admin", "staff"})


@login_required
@user_passes_test(_is_student_or_parent)
def apply_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
        return redirect("enrollment:my_requests")

    if request.method == "POST":
        form = EnrollmentRequestForm(request.POST)
        if form.is_valid():
            enrollment_request = form.save(commit=False)
            enrollment_request.student = request.user
            enrollment_request.course = course
            try:
                enrollment_request.save()
                messages.success(request, "Enrollment request submitted successfully.")
                return redirect("enrollment:my_requests")
            except IntegrityError:
                messages.warning(request, "A pending request for this course already exists.")
    else:
        form = EnrollmentRequestForm(initial={"course": course})

    form.fields["course"].queryset = Course.objects.filter(id=course.id)
    form.fields["course"].disabled = True
    return render(request, "enrollment/apply.html", {"form": form, "course": course})


@login_required
@user_passes_test(_is_student_or_parent)
def my_requests(request):
    requests_qs = EnrollmentRequest.objects.filter(student=request.user).select_related("course")
    return render(request, "enrollment/my_requests.html", {"requests": requests_qs})


@login_required
@user_passes_test(_is_staff_or_admin)
def request_list(request):
    requests_qs = EnrollmentRequest.objects.select_related("student", "course")
    return render(request, "enrollment/request_list.html", {"requests": requests_qs})


@login_required
@user_passes_test(_is_staff_or_admin)
def approve_request(request, id):
    enrollment_request = get_object_or_404(EnrollmentRequest, id=id)

    if enrollment_request.status != EnrollmentRequest.Status.PENDING:
        messages.warning(request, "Only pending requests can be approved.")
        return redirect("enrollment:request_list")

    try:
        with transaction.atomic():
            Enrollment.objects.get_or_create(student=enrollment_request.student, course=enrollment_request.course)
            enrollment_request.status = EnrollmentRequest.Status.APPROVED
            enrollment_request.save(update_fields=["status"])
    except IntegrityError:
        messages.error(request, "Enrollment already exists for this student and course.")
    else:
        messages.success(request, "Enrollment request approved and enrollment created.")

    return redirect("enrollment:request_list")


@login_required
@user_passes_test(_is_staff_or_admin)
def reject_request(request, id):
    enrollment_request = get_object_or_404(EnrollmentRequest, id=id)

    if enrollment_request.status != EnrollmentRequest.Status.PENDING:
        messages.warning(request, "Only pending requests can be rejected.")
    else:
        enrollment_request.status = EnrollmentRequest.Status.REJECTED
        enrollment_request.save(update_fields=["status"])
        messages.success(request, "Enrollment request rejected.")

    return redirect("enrollment:request_list")
