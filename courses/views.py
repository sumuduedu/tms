from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CourseForm, ModuleForm
from .models import Course


def user_can_manage_courses(user):
    role = getattr(user, "role", None)
    return bool(user.is_authenticated and (user.is_superuser or user.is_staff or role in {"admin", "staff"}))

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user_can_manage_courses(user)


class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(status=Course.Status.PUBLISHED).select_related("created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_courses"] = user_can_manage_courses(self.request.user)
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        queryset = Course.objects.select_related("created_by").prefetch_related("modules")
        if self.request.user.is_authenticated:
            if user_can_manage_courses(self.request.user):
                return queryset
        return queryset.filter(status=Course.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_courses"] = user_can_manage_courses(self.request.user)
        return context


class CourseCreateView(StaffRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CourseUpdateView(StaffRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"


class CourseDeleteView(StaffRequiredMixin, DeleteView):
    model = Course
    template_name = "courses/course_confirm_delete.html"
    success_url = reverse_lazy("courses:course_list")


class ModuleCreateView(StaffRequiredMixin, CreateView):
    form_class = ModuleForm
    template_name = "courses/course_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        module = form.save(commit=False)
        module.course = self.course
        module.save()
        return redirect("courses:course_detail", pk=self.course.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        context["module_mode"] = True
        return context
