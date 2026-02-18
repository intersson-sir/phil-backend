# Data migration: create test user (phil_demo / PhilDemo2026)

from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_test_user(apps, schema_editor):
    User = apps.get_model("auth", "User")
    if User.objects.filter(username="phil_demo").exists():
        return
    user = User(
        username="phil_demo",
        email="phil_demo@example.com",
        password=make_password("PhilDemo2026"),
        is_staff=False,
        is_active=True,
    )
    user.save()


def remove_test_user(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User.objects.filter(username="phil_demo").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "__first__"),
    ]

    operations = [
        migrations.RunPython(create_test_user, remove_test_user),
    ]
