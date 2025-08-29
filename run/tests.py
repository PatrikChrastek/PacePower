import pytest
from datetime import date
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from run.models import Run, Profile, TrainingPlan, PlannedRun, ensure_default_zones, Tag


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
    UserModel = get_user_model()
    u = UserModel.objects.create_user(username="patriktest", password="patriktest")
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
    UserModel = get_user_model()
    u = UserModel.objects.create_user(username="patriktest2", password="patriktest2")
    assert client.login(username="patriktest2", password="patriktest2") is True

    res = client.get(reverse("run_list"))
    assert res.status_code == 200


# test run_detail requires login
@pytest.mark.django_db
def test_run_detail_needs_login(client):
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


# defaults created for a new profile
@pytest.mark.django_db
def test_profile_defaults_are_used(client):
    user = User.objects.create_user(username="patriktest5", password="patriktest5")
    profile = Profile.objects.create(user=user)
    ensure_default_zones(profile)

    zones = list(
        profile.zones.order_by("zone_number").values_list("zone_number", "hr_min", "hr_max")
    )
    assert len(zones) == 5
    assert zones[0] == (1, 108, 133)
    assert zones[-1] == (5, 167, 193)


# editing zones via inline formset
@pytest.mark.django_db
def test_profile_edit_view_updates_ranges(client):
    user = User.objects.create_user(username="patriktest6", password="patriktest6")
    client.login(username="patriktest6", password="patriktest6")
    profile = Profile.objects.create(user=user)
    ensure_default_zones(profile)

    qs = profile.zones.order_by("zone_number")
    total = qs.count()

    form_data = {
        "form-TOTAL_FORMS": str(total),
        "form-INITIAL_FORMS": str(total),
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
    }
    for i, z in enumerate(qs):
        form_data[f"form-{i}-id"] = str(z.id)
        form_data[f"form-{i}-zone_number"] = str(z.zone_number)
        form_data[f"form-{i}-hr_min"] = "100" if z.zone_number == 1 else str(z.hr_min)
        form_data[f"form-{i}-hr_max"] = str(z.hr_max)

    resp = client.post(reverse("profile_edit"), data=form_data)
    assert resp.status_code in (301, 302)

    z1 = profile.zones.get(zone_number=1)
    assert z1.hr_min == 100


# test that plan list is login-only and shows user's plans
@pytest.mark.django_db
def test_training_plan_list_view(client):
    u1 = User.objects.create_user(username="patriktest7", password="patriktest7")
    u2 = User.objects.create_user(username="patriktest8", password="patriktest8")
    TrainingPlan.objects.create(user=u1, name="Plan A")
    TrainingPlan.objects.create(user=u2, name="Plan B")

    resp = client.get(reverse("plan_list"))
    assert resp.status_code in (301, 302)

    client.login(username="patriktest7", password="patriktest7")
    resp = client.get(reverse("plan_list"))
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "Plan A" in content
    assert "Plan B" not in content


# test that valid POST creates a planned run and redirects
@pytest.mark.django_db
def test_planned_run_create_post_valid(client):
    user = User.objects.create_user(username="patriktest9", password="patriktest9")
    client.login(username="patriktest9", password="patriktest9")
    plan = TrainingPlan.objects.create(user=user, name="My Plan")

    form_data = {
        "plan": plan.id,
        "date": date(2025, 8, 21),
        "run_type": "EASY",
        "distance_km": 10.0,
        "pace_target": "5:30",
        "notes": "easy planned",
    }
    resp = client.post(reverse("planned_run_create"), data=form_data)
    assert resp.status_code in (301, 302)
    assert PlannedRun.objects.filter(plan=plan, date=date(2025, 8, 21)).exists()


# create run with tags
@pytest.mark.django_db
def test_run_create_with_tags(client):
    u = User.objects.create_user(username="patriktest10", password="patriktest10")
    client.login(username="patriktest10", password="patriktest10")
    t1 = Tag.objects.create(user=u, name="trail")
    t2 = Tag.objects.create(user=u, name="morning")

    form_data = {
        "date": date(2025, 8, 22),
        "run_type": "EASY",
        "distance_km": "6.0",
        "pace_min_km": "5:45",
        "heart_rate": "",
        "zone": "",
        "notes": "tagged run",
        "tags": [str(t1.id), str(t2.id)],
    }
    resp = client.post(reverse("run_create"), data=form_data)
    assert resp.status_code in (301, 302)
    r = Run.objects.get(user=u, date=date(2025, 8, 22))
    names = set(r.tags.values_list("name", flat=True))
    assert names == {"trail", "morning"}


# filter run_list by tag
@pytest.mark.django_db
def test_run_list_filter_by_tag(client):
    u = User.objects.create_user(username="patriktest11", password="patriktest11")
    client.login(username="patriktest11", password="patriktest11")
    tag_trail = Tag.objects.create(user=u, name="trail")
    tag_city = Tag.objects.create(user=u, name="city")

    r1 = Run.objects.create(user=u, date=date(2025, 8, 10), run_type="EASY", distance_km=5.0, pace_min_km="6:00")
    r1.tags.add(tag_trail)
    r2 = Run.objects.create(user=u, date=date(2025, 8, 11), run_type="EASY", distance_km=7.0, pace_min_km="5:50")
    r2.tags.add(tag_city)

    resp = client.get(reverse("run_list"), {"tag": tag_trail.id})
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "2025-08-10" in body
    assert "2025-08-11" not in body


# test login required for viewing plan list
@pytest.mark.django_db
def test_plan_list_requires_login(client):
    resp = client.get(reverse("plan_list"))
    assert resp.status_code in (301, 302)


# test only own plans are visible for logged-in user
@pytest.mark.django_db
def test_plan_list_auth_ok_and_own_plans_only(client):
    u1 = User.objects.create_user(username="patriktestA", password="patriktestA")
    u2 = User.objects.create_user(username="patriktestB", password="patriktestB")
    TrainingPlan.objects.create(user=u1, name="pA Plan")
    TrainingPlan.objects.create(user=u2, name="pB Plan")
    client.login(username="patriktestA", password="patriktestA")
    resp = client.get(reverse("plan_list"))
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "pA Plan" in body
    assert "pB Plan" not in body


# test login required for creating planned run
@pytest.mark.django_db
def test_planned_run_create_requires_login(client):
    resp = client.get(reverse("planned_run_create"))
    assert resp.status_code in (301, 302)


# test form is shown to logged-in user when creating planned run
@pytest.mark.django_db
def test_planned_run_create_get_ok(client):
    u = User.objects.create_user(username="patriktest12", password="patriktest12")
    client.login(username="patriktest12", password="patriktest12")
    TrainingPlan.objects.create(user=u, name="Plan X")
    resp = client.get(reverse("planned_run_create"))
    assert resp.status_code == 200


# test login required for calendar view
def test_calendar_view_requires_login(client):
    resp = client.get(reverse("calendar_view"))
    assert resp.status_code in (301, 302)


# test empty calendar shows empty message to logged-in user
@pytest.mark.django_db
def test_calendar_view_auth_empty_month(client):
    u = User.objects.create_user(username="patriktest13", password="patriktest13")
    client.login(username="patriktest13", password="patriktest13")
    resp = client.get(reverse("calendar_view"))
    assert resp.status_code == 200
    assert "No planned runs this month." in resp.content.decode()


# test planned run appears in calendar for logged-in user
@pytest.mark.django_db
def test_calendar_view_auth_with_item(client):
    u = User.objects.create_user(username="patriktest14", password="patriktest14")
    client.login(username="patriktest14", password="patriktest14")
    plan = TrainingPlan.objects.create(user=u, name="My Calendar Plan")
    PlannedRun.objects.create(user=u, plan=plan, date=date.today(), run_type="EASY", distance_km=5.0)
    resp = client.get(reverse("calendar_view"))
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "My Calendar Plan" in body
