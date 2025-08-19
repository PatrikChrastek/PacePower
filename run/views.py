from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RunForm, ProfileForm
from .models import Run, Profile


# display homepage
def home_view(request):
    return render(request, "run/home.html")


# create new run
@login_required
def run_create_view(request):
    if request.method == "POST":
        form = RunForm(request.POST)
        if form.is_valid():
            run = form.save(commit=False)
            run.user = request.user
            run.save()
            return redirect("run_list")
    else:
        form = RunForm()
    return render(request, "run/run_form.html", {"form": form})


# list runs
@login_required
def run_list_view(request):
    runs = Run.objects.filter(user=request.user).order_by("-date")
    return render(request, "run/run_list.html", {"runs": runs})


# Show a single run
@login_required
def run_detail_view(request, pk: int):
    run = get_object_or_404(Run, pk=pk, user=request.user)
    return render(request, "run/run_detail.html", {"run": run})


# Edit HR zones in user profile
@login_required
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "run/profile_form.html", {"form": form})
