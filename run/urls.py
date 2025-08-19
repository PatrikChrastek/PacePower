from django.urls import path
from . import views


urlpatterns = [
    path("runs/", views.run_list_view, name="run_list"),
    path("runs/new/", views.run_create_view, name="run_create"),
    path("runs/<int:pk>/", views.run_detail_view, name="run_detail"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
]
