from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render, redirect

from .forms import CompetencyRecordForm
from .models import Competency, CompetencyRecord, NCSUnit, Task


def _require_role(user, allowed_roles):
    role = getattr(user, "role", None)
    if role not in allowed_roles and not user.is_staff and not user.is_superuser:
        raise PermissionDenied


@login_required
def ncsunit_list(request):
    _require_role(request.user, {"admin", "staff"})
    units = NCSUnit.objects.select_related("module").all()
    return render(request, "competency/ncs_list.html", {"units": units})


@login_required
def competency_list(request):
    _require_role(request.user, {"admin", "staff"})
    competencies = Competency.objects.select_related("unit").all()
    return render(request, "competency/competency_list.html", {"competencies": competencies})


@login_required
def task_list(request):
    _require_role(request.user, {"admin", "staff"})
    tasks = Task.objects.select_related("competency", "competency__unit").all()
    return render(request, "competency/task_list.html", {"tasks": tasks})


@login_required
def assess_competency(request, student_id, competency_id):
    _require_role(request.user, {"teacher"})
    competency = get_object_or_404(Competency, pk=competency_id)
    student_model = request.user.__class__
    student = get_object_or_404(student_model, pk=student_id)

    record, _ = CompetencyRecord.objects.get_or_create(
        student=student,
        competency=competency,
        defaults={"assessed_by": request.user},
    )

    if request.method == "POST":
        form = CompetencyRecordForm(request.POST, instance=record)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.assessed_by = request.user
            saved.save()
            return redirect(request.path)
    else:
        form = CompetencyRecordForm(instance=record)

    return render(request, "competency/assess_form.html", {"form": form, "student": student, "competency": competency})


@login_required
def competency_records_by_batch(request, batch_id):
    _require_role(request.user, {"teacher"})
    records = CompetencyRecord.objects.select_related("student", "competency", "competency__unit")
    try:
        records = records.filter(student__batch_id=batch_id)
    except Exception:
        pass
    return render(request, "competency/student_progress.html", {"records": records, "batch_id": batch_id, "is_teacher": True})


@login_required
def my_competencies(request):
    _require_role(request.user, {"student"})

    units = NCSUnit.objects.prefetch_related(
        Prefetch(
            "competencies",
            queryset=Competency.objects.prefetch_related("tasks").all(),
        )
    )
    records = {
        r.competency_id: r
        for r in CompetencyRecord.objects.select_related("competency").filter(student=request.user)
    }

    progress = []
    for unit in units:
        comps = []
        for comp in unit.competencies.all():
            comps.append((comp, records.get(comp.id)))
        progress.append((unit, comps))

    return render(request, "competency/student_progress.html", {"progress": progress, "is_teacher": False})
