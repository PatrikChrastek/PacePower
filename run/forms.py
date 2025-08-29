from django import forms
from django.forms import inlineformset_factory
from .models import Run, validate_mm_ss, Profile, TrainingPlan, PlannedRun, HeartRateZone


# form for creating and editing runs
class RunForm(forms.ModelForm):
    pace_min_km = forms.CharField(max_length=5, help_text="mm:ss (e.g. 5:30)")

    class Meta:
        model = Run
        fields = ["date", "run_type", "distance_km", "pace_min_km", "heart_rate", "zone", "notes", "tags"]
        
    # validate pace_min_km field
    def clean_pace_min_km(self):
        value = self.cleaned_data["pace_min_km"]
        validate_mm_ss(value)
        return value

# simple profile form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = []

# single zone form
class HeartRateZoneForm(forms.ModelForm):
    class Meta:
        model = HeartRateZone
        fields = ["zone_number", "hr_min", "hr_max"]

# formset for editing multiple zones
HeartRateZoneFormSet = inlineformset_factory(
    parent_model=Profile,
    model=HeartRateZone,
    form=HeartRateZoneForm,
    fields=["zone_number", "hr_min", "hr_max"],
    extra=0,
    can_delete=False,
)


# form to create and edit planned runs
class PlannedRunForm(forms.ModelForm):
    pace_target = forms.CharField(max_length=5, required=False, help_text="mm:ss (optional)")

    class Meta:
        model = PlannedRun
        fields = ["plan", "date", "run_type", "distance_km", "pace_target", "notes"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["plan"].required = False
        if user is not None:
            from .models import TrainingPlan
            self.fields["plan"].queryset = TrainingPlan.objects.filter(user=user)

    def clean_pace_target(self):
        value = self.cleaned_data.get("pace_target") or ""
        if value:
            validate_mm_ss(value)
        return value
    

# simple form to create a plan
class TrainingPlanForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        fields = ["name", "description", "start_date"]


