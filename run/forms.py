from django import forms
from .models import Run, validate_mm_ss, Profile


# form for creating and editing runs
class RunForm(forms.ModelForm):
    pace_min_km = forms.CharField(max_length=5, help_text="mm:ss (e.g. 5:30)")
    
    class Meta:
        model = Run
        fields = ["date", "run_type", "distance_km", "pace_min_km", "heart_rate", "zone", "notes"]

    # validate pace_min_km field
    def clean_pace_min_km(self):
        value = self.cleaned_data["pace_min_km"]
        validate_mm_ss(value)
        return value


# Form for editing HR zones as ranges
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "hr_zone1_min", "hr_zone1_max",
            "hr_zone2_min", "hr_zone2_max",
            "hr_zone3_min", "hr_zone3_max",
            "hr_zone4_min", "hr_zone4_max",
            "hr_zone5_min", "hr_zone5_max",
        ]
        