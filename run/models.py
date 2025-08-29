from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import re


RUN_TYPE_CHOICES = [
    ("RUN", "Run"),
    ("EASY", "Easy"),
    ("TEMPO", "Tempo"),
    ("INTERVAL", "Interval"),
    ("RECOVERY", "Recovery"),
    ("FARTLEK", "Fartlek"),
    ("LONG", "Long"),
    ("RACE", "Race"),
    ("OTHER", "Other"),
]


# Validate 'mm:ss' string format
def validate_mm_ss(value: str):
    if not re.match(r"^\d{1,2}:\d{2}$", value):
        raise ValueError("Use 'mm:ss' format, e.g. 5:30")


# Tag owned by a user
class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=30)

    class Meta:
        unique_together = (("user", "name"),)
        ordering = ["name"]

    def __str__(self):
        return self.name


# Run model
class Run(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="run_trainings")
    date = models.DateField()
    run_type = models.CharField(max_length=10, choices=RUN_TYPE_CHOICES)
    distance_km = models.FloatField(validators=[MinValueValidator(0.01)])
    pace_min_km = models.CharField(max_length=5, validators=[validate_mm_ss])
    heart_rate = models.CharField(max_length=20, blank=True)
    zone = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="runs")

    class Meta:
        ordering = ["-date"]

    # Readable representation
    def __str__(self):
        return f"{self.user.username} {self.date} {self.distance_km} km @ {self.pace_min_km}"

    # Get pace in seconds
    @property
    def pace_seconds(self) -> int:
        m, s = self.pace_min_km.split(":")
        return int(m) * 60 + int(s)
    

# User profile - zones in separate records
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return f"{self.user.username}'s profile"

class HeartRateZone(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="zones")
    zone_number = models.PositiveIntegerField()
    hr_min = models.PositiveIntegerField()
    hr_max = models.PositiveIntegerField()

    class Meta:
        ordering = ["zone_number"]
        unique_together = (("profile", "zone_number"),)

    def __str__(self):
        return f"Zone {self.zone_number}: {self.hr_min}-{self.hr_max} bpm"

    def clean(self):
        if self.hr_min > self.hr_max:
            from django.core.exceptions import ValidationError
            raise ValidationError({"hr_max": "Max must be >= Min"})


DEFAULT_ZONES = [
    (1, 108, 133),
    (2, 134, 148),
    (3, 149, 158),
    (4, 159, 166),
    (5, 167, 193),
]


# Create defaults for a profile if none exist
def ensure_default_zones(profile):
    if not profile.zones.exists():
        from .models import HeartRateZone
        HeartRateZone.objects.bulk_create([
            HeartRateZone(profile=profile, zone_number=n, hr_min=lo, hr_max=hi)
            for (n, lo, hi) in DEFAULT_ZONES
        ])


# Training plan owned by a user
class TrainingPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="training_plans")
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    

# Single planned run inside a plan
class PlannedRun(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="planned_runs")
    plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    date = models.DateField()
    run_type = models.CharField(max_length=10, choices=RUN_TYPE_CHOICES)
    distance_km = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.01)])
    pace_target = models.CharField(max_length=5, blank=True, validators=[validate_mm_ss])
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.plan.name} - {self.date} {self.run_type}"
    
