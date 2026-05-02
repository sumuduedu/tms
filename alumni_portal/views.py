from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AlumniProfileForm, JobPostForm
from .models import AlumniProfile, JobPost


def _is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, "role", "") in {"admin", "staff"})


def _can_post_job(user):
    return user.is_authenticated and (_is_admin_or_staff(user) or hasattr(user, "alumni_profile") or getattr(user, "role", "") == "alumni")


@user_passes_test(_is_admin_or_staff)
def alumni_list(request):
    alumni = AlumniProfile.objects.select_related("user", "course", "batch").all()
    return render(request, "alumni/alumni_list.html", {"alumni": alumni})


@login_required
def my_profile(request):
    profile = get_object_or_404(AlumniProfile.objects.select_related("user", "course", "batch"), user=request.user)
    return render(request, "alumni/profile.html", {"profile": profile})


@login_required
def update_profile(request):
    profile = get_object_or_404(AlumniProfile, user=request.user)
    if not (_is_admin_or_staff(request.user) or profile.user_id == request.user.id):
        raise PermissionDenied

    if request.method == "POST":
        form = AlumniProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("alumni:my_profile")
    else:
        form = AlumniProfileForm(instance=profile)

    return render(request, "alumni/profile_form.html", {"form": form, "profile": profile})


def job_list(request):
    queryset = JobPost.objects.select_related("posted_by")
    if _is_admin_or_staff(request.user):
        jobs = queryset
    else:
        jobs = queryset.filter(is_active=True)
    return render(request, "jobs/job_list.html", {"jobs": jobs})


def job_detail(request, pk):
    job = get_object_or_404(JobPost, pk=pk)
    if not job.is_active and not _is_admin_or_staff(request.user):
        raise PermissionDenied
    return render(request, "jobs/job_detail.html", {"job": job})


@login_required
def job_create(request):
    if not _can_post_job(request.user):
        raise PermissionDenied
    if request.method == "POST":
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect("alumni:job_detail", pk=job.pk)
    else:
        form = JobPostForm()
    return render(request, "jobs/job_form.html", {"form": form, "is_create": True})


@login_required
def job_update(request, pk):
    job = get_object_or_404(JobPost, pk=pk)
    can_manage = _is_admin_or_staff(request.user) or job.posted_by_id == request.user.id
    if not can_manage:
        raise PermissionDenied

    if request.method == "POST":
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect("alumni:job_detail", pk=job.pk)
    else:
        form = JobPostForm(instance=job)
    return render(request, "jobs/job_form.html", {"form": form, "job": job, "is_create": False})


@login_required
def job_delete(request, pk):
    job = get_object_or_404(JobPost, pk=pk)
    can_manage = _is_admin_or_staff(request.user) or job.posted_by_id == request.user.id
    if not can_manage:
        raise PermissionDenied

    if request.method == "POST":
        job.delete()
        return redirect("alumni:job_list")
    return render(request, "jobs/job_detail.html", {"job": job, "confirm_delete": True})
