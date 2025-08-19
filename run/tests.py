import pytest
from datetime import date
from django.urls import reverse
from django.contrib.auth import get_user_model
from run.models import Run
from django.contrib.auth.models import User
from run.models import Profile


# test home returns 200
@pytest.mark.django_db
def test_home_ok(client):
    res = client.get(reverse("home"))
    assert res.status_code == 200


# test home shows expected title
@pytest.mark.django_db
def test_home_shows_title(client):
    res = client.get(reverse("home"))
    body = res.content.decode()
    assert "Pace" in body or "Run" in body


# test run_create requires login
@pytest.mark.django_db
def test_run_create_needs_login(client):
    res = client.get(reverse("run_create"))
    assert res.status_code in (301, 302)


# test valid POST creates a run and redirects
@pytest.mark.django_db
def test_run_create_ok_redirect_and_saved(client):
    User = get_user_model()
    u = User.objects.create_user(username="patriktest", password="patriktest")
    assert client.login(username="patriktest", password="patriktest") is True

    form_data = {
        "date": date(2025, 8, 15),
        "run_type": "EASY",
        "distance_km": "10.0",
        "pace_min_km": "5:30",
        "heart_rate": "140-150",
        "zone": "Z2",
        "notes": "test run",
    }
    res = client.post(reverse("run_create"), data=form_data)
    assert res.status_code in (301, 302)
    assert Run.objects.filter(user=u, distance_km="10.0").exists()


# test run_list requires login
@pytest.mark.django_db
def test_run_list_needs_login(client):
    res = client.get(reverse("run_list"))
    assert res.status_code in (301, 302)


# test run_list works when logged in
@pytest.mark.django_db
def test_run_list_ok_when_logged_in(client):
    User = get_user_model()
    u = User.objects.create_user(username="patriktest2", password="patriktest2")
    assert client.login(username="patriktest2", password="patriktest2") is True

    res = client.get(reverse("run_list"))
    assert res.status_code == 200


# test run_detail requires login
@pytest.mark.django_db
def test_run_detail_needs_login(client):
    User = get_user_model()
    owner = User.objects.create_user(username="patriktest3", password="patriktest3")
    r = Run.objects.create(
        user=owner,
        date=date(2025, 8, 16),
        run_type="EASY",
        distance_km="5.0",
        pace_min_km="5:30",
    )
    res = client.get(reverse("run_detail", args=[r.pk]))
    assert res.status_code in (301, 302)


# test run_detail shows my own run
@pytest.mark.django_db
def test_run_detail_own_ok(client):
    User = get_user_model()
    u = User.objects.create_user(username="patriktest4", password="patriktest4")
    assert client.login(username="patriktest4", password="patriktest4") is True

    my_run = Run.objects.create(
        user=u,
        date=date(2025, 8, 16),
        run_type="EASY",
        distance_km="8.0",
        pace_min_km="5:15",
    )
    res = client.get(reverse("run_detail", args=[my_run.pk]))
    assert res.status_code == 200
    assert "8.0" in res.content.decode()


# test that profile should use default zones when empty
@pytest.mark.django_db
def test_profile_defaults_are_used(client):
    user = User.objects.create_user(username="patriktest5", password="patriktest5")
    profile = Profile.objects.create(user=user)
    assert profile.hr_zone1_min == 108
    assert profile.hr_zone1_max == 133
    assert profile.hr_zone5_min == 167
    assert profile.hr_zone5_max == 193


# test that saving form should update HR zones
@pytest.mark.django_db
def test_profile_edit_view_updates_ranges(client):
    user = User.objects.create_user(username="patriktest6", password="patriktest6")
    client.login(username="patriktest6", password="patriktest6")
    profile = Profile.objects.create(user=user)
    form_data = {
        "hr_zone1_min": 100, "hr_zone1_max": 130,
        "hr_zone2_min": 131, "hr_zone2_max": 145,
        "hr_zone3_min": 146, "hr_zone3_max": 155,
        "hr_zone4_min": 156, "hr_zone4_max": 165,
        "hr_zone5_min": 166, "hr_zone5_max": 190,
    }
    resp = client.post(reverse("profile_edit"), data=form_data)
    assert resp.status_code in (301, 302)
    profile.refresh_from_db()
    assert profile.hr_zone1_min == 100
    assert profile.hr_zone5_max == 190


