"""
Create a test user for checking auth.
Usage: python manage.py create_test_user
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create test user for auth (login: phil_demo, password: PhilDemo2026)'

    def handle(self, *args, **options):
        username = 'phil_demo'
        password = 'PhilDemo2026'
        email = 'phil_demo@example.com'

        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': False,
                'is_active': True,
            },
        )
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Test user created. Login: {username}, Password: {password}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Test user updated. Login: {username}, Password: {password}'
                )
            )
