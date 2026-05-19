from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ExerciseForm, ExerciseResourceFormSet
from .models import Exercise


class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "Teacher"


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "Student"


class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = "exercises/exercise_list.html"


class ExerciseDetailView(LoginRequiredMixin, DetailView):
    model = Exercise
    template_name = "exercises/exercise_detail.html"


class ExerciseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = "exercises/exercise_form.html"
    success_url = reverse_lazy("exercises:manage")

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        response = super().form_valid(form)
        formset = ExerciseResourceFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = ExerciseResourceFormSet(self.request.POST or None, self.request.FILES or None)
        return context


class ExerciseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = "exercises/exercise_form.html"
    success_url = reverse_lazy("exercises:manage")

    def get_queryset(self):
        return Exercise.objects.filter(teacher=self.request.user)


class ExerciseDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Exercise
    template_name = "exercises/exercise_confirm_delete.html"
    success_url = reverse_lazy("exercises:manage")

    def get_queryset(self):
        return Exercise.objects.filter(teacher=self.request.user)


class ManageExerciseListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Exercise
    template_name = "exercises/manage_exercises.html"

    def get_queryset(self):
        return Exercise.objects.filter(teacher=self.request.user)
