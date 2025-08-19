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
    

# User profile with HR zones
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    hr_zone1_min = models.PositiveIntegerField(default=108)
    hr_zone1_max = models.PositiveIntegerField(default=133)
    hr_zone2_min = models.PositiveIntegerField(default=134)
    hr_zone2_max = models.PositiveIntegerField(default=148)
    hr_zone3_min = models.PositiveIntegerField(default=149)
    hr_zone3_max = models.PositiveIntegerField(default=158)
    hr_zone4_min = models.PositiveIntegerField(default=159)
    hr_zone4_max = models.PositiveIntegerField(default=166)
    hr_zone5_min = models.PositiveIntegerField(default=167)
    hr_zone5_max = models.PositiveIntegerField(default=193)

    def __str__(self):
        return f"{self.user.username}'s profile"