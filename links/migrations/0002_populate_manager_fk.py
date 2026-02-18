# Data migration: convert manager (string) to manager_fk (FK)

from django.db import migrations
from django.utils.text import slugify


def unique_email_for_name(apps, name):
    """Generate unique email for a manager name (for imported data)."""
    Manager = apps.get_model('managers', 'Manager')
    base = (slugify(name) or 'manager')[:50]
    email = f'{base}@imported.local'
    counter = 0
    while Manager.objects.filter(email=email).exists():
        counter += 1
        email = f'{base}{counter}@imported.local'
    return email


def populate_manager_fk(apps, schema_editor):
    NegativeLink = apps.get_model('links', 'NegativeLink')
    Manager = apps.get_model('managers', 'Manager')
    for link in NegativeLink.objects.exclude(manager__isnull=True).exclude(manager=''):
        name = (link.manager or '').strip()
        if not name:
            continue
        email = unique_email_for_name(apps, name)
        manager_obj, _ = Manager.objects.get_or_create(
            email=email,
            defaults={'name': name, 'is_active': True},
        )
        link.manager_fk = manager_obj
        link.save(update_fields=['manager_fk'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_manager_fk, noop),
    ]
