from django.contrib import admin
from .models import Run, Profile, TrainingPlan, PlannedRun, HeartRateZone, Tag


# Admin access for classes below
admin.site.register(Run)
admin.site.register(Profile)
admin.site.register(TrainingPlan)
admin.site.register(PlannedRun)
admin.site.register(HeartRateZone)
admin.site.register(Tag)
