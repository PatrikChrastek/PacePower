from django.contrib import admin
from .models import Run, Profile

# Admin access for classes below
admin.site.register(Run)
admin.site.register(Profile)
