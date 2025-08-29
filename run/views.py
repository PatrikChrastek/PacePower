from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RunForm, ProfileForm, PlannedRunForm, TrainingPlanForm, HeartRateZoneFormSet
from .models import Run, Profile, TrainingPlan, PlannedRun, ensure_default_zones, Tag
from datetime import date as _date, timedelta
import calendar


# display homepage
def home_view(request):
    return render(request, "run/home.html")


# create new run
@login_required
def run_create_view(request):
    if request.method == "POST":
        form = RunForm(request.POST)
        form.fields["tags"].queryset = Tag.objects.filter(user=request.user)
        if form.is_valid():
            run = form.save(commit=False)
            run.user = request.user
            run.save()
            form.save_m2m()
            return redirect("run_list")
    else:
        form = RunForm()
        form.fields["tags"].queryset = Tag.objects.filter(user=request.user)
    return render(request, "run/run_form.html", {"form": form})


# list runs
@login_required
def run_list_view(request):
    runs = Run.objects.filter(user=request.user).prefetch_related("tags").order_by("-date")
    tag_id = request.GET.get("tag")
    if tag_id:
        runs = runs.filter(tags__id=tag_id)
    return render(request, "run/run_list.html", {"runs": runs})


# show a single run
@login_required
def run_detail_view(request, pk: int):
    run = get_object_or_404(Run, pk=pk, user=request.user)
    return render(request, "run/run_detail.html", {"run": run})


# edit HR zones in user profile
@login_required
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    ensure_default_zones(profile)

    prefix = "form"

    if request.method == "POST":
        pform = ProfileForm(request.POST, instance=profile)
        formset = HeartRateZoneFormSet(request.POST, instance=profile, prefix=prefix)
        if formset.is_valid():
            pform.save()
            formset.save()
            return redirect("home")
    else:
        pform = ProfileForm(instance=profile)
        formset = HeartRateZoneFormSet(instance=profile, prefix=prefix)

    return render(request, "run/profile_form.html", {"form": pform, "formset": formset})



# list user's training plans
@login_required
def plan_list_view(request):
    plans = TrainingPlan.objects.filter(user=request.user).order_by("name")
    return render(request, "run/plan_list.html", {"plans": plans})


# create a planned run
@login_required
def planned_run_create_view(request):
    if request.method == "POST":
        form = PlannedRunForm(request.POST, user=request.user)
        if form.is_valid():
            planned = form.save(commit=False)
            planned.user = request.user
            if planned.plan and planned.plan.user != request.user:
                return redirect("plan_list")
            planned.save()
            return redirect("calendar_view")
    else:
        form = PlannedRunForm(user=request.user)
    return render(request, "run/planned_run_form.html", {"form": form})



# month calendar with user's planned runs
@login_required
def calendar_view(request):
    today = _date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    first_day = _date(year, month, 1)
    last_day = _date(year, month, calendar.monthrange(year, month)[1])

    items = PlannedRun.objects.filter(
        user=request.user,
        date__gte=first_day,
        date__lte=last_day,
    ).select_related("plan").order_by("date")

    prev_month = (first_day - timedelta(days=1)).replace(day=1)
    next_month_first = (last_day + timedelta(days=1)).replace(day=1)

    ctx = {
        "year": year,
        "month": month,
        "items": items,
        "prev_year": prev_month.year,
        "prev_month": prev_month.month,
        "next_year": next_month_first.year,
        "next_month": next_month_first.month,
    }
    return render(request, "run/calendar.html", ctx)
