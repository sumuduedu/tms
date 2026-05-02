from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from batch_management.models import Batch

from .forms import LessonPlanForm, TimetableForm
from .models import LessonPlan, Timetable


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        user = self.request.user
        if user.is_staff:
            return True
        return getattr(user, "role", None) in self.allowed_roles


class TimetableListView(LoginRequiredMixin, ListView):
    template_name = "planning/timetable_list.html"
    context_object_name = "timetable_entries"

    def get_queryset(self):
        self.batch = get_object_or_404(Batch, pk=self.kwargs["batch_id"])
        qs = Timetable.objects.filter(batch=self.batch)

        role = getattr(self.request.user, "role", None)
        if role == "student":
            return qs
        if role == "teacher":
            return qs.filter(batch__teacher=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["batch"] = self.batch
        return context


class TimetableCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Timetable
    form_class = TimetableForm
    template_name = "planning/timetable_form.html"
    allowed_roles = ("admin",)

    def dispatch(self, request, *args, **kwargs):
        self.batch = get_object_or_404(Batch, pk=self.kwargs["batch_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.batch = self.batch
        messages.success(self.request, "Timetable entry created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("planning:timetable_list", kwargs={"batch_id": self.batch.id})


class TimetableUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Timetable
    form_class = TimetableForm
    template_name = "planning/timetable_form.html"
    allowed_roles = ("admin",)

    def get_success_url(self):
        messages.success(self.request, "Timetable entry updated.")
        return reverse_lazy("planning:timetable_list", kwargs={"batch_id": self.object.batch_id})


class TimetableDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Timetable
    template_name = "planning/timetable_form.html"
    allowed_roles = ("admin",)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        batch_id = self.object.batch_id
        self.object.delete()
        messages.success(self.request, "Timetable entry deleted.")
        return redirect("planning:timetable_list", batch_id=batch_id)


class LessonPlanListView(LoginRequiredMixin, ListView):
    template_name = "planning/lessonplan_list.html"
    context_object_name = "lessonplans"

    def get_queryset(self):
        self.batch = get_object_or_404(Batch, pk=self.kwargs["batch_id"])
        qs = LessonPlan.objects.select_related("created_by", "timetable").filter(batch=self.batch)
        role = getattr(self.request.user, "role", None)
        if self.request.user.is_staff:
            return qs
        if role == "teacher":
            return qs.filter(batch__teacher=self.request.user)
        if role == "student":
            return qs
        return qs.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["batch"] = self.batch
        return context


class LessonPlanCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = LessonPlan
    form_class = LessonPlanForm
    template_name = "planning/lessonplan_form.html"
    allowed_roles = ("teacher",)

    def dispatch(self, request, *args, **kwargs):
        self.batch = get_object_or_404(Batch, pk=self.kwargs["batch_id"])
        if request.user.is_staff:
            return redirect("planning:lessonplan_list", batch_id=self.batch.id)
        if getattr(request.user, "role", None) != "teacher" or self.batch.teacher_id != request.user.id:
            messages.error(request, "You are not assigned to this batch.")
            return redirect("planning:lessonplan_list", batch_id=self.batch.id)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["batch"] = self.batch
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.batch = self.batch
        form.instance.created_by = self.request.user
        messages.success(self.request, "Lesson plan created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("planning:lessonplan_detail", kwargs={"pk": self.object.id})


class LessonPlanDetailView(LoginRequiredMixin, DetailView):
    model = LessonPlan
    template_name = "planning/lessonplan_detail.html"
    context_object_name = "lessonplan"

    def get_queryset(self):
        qs = LessonPlan.objects.select_related("batch", "created_by", "timetable")
        if self.request.user.is_staff:
            return qs
        role = getattr(self.request.user, "role", None)
        if role == "teacher":
            return qs.filter(batch__teacher=self.request.user)
        if role == "student":
            return qs
        return qs.none()
