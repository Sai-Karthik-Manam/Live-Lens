from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Create default role groups: Customer, Admin, Support Agent'

    def handle(self, *args, **options):
        roles = ['Customer', 'Admin', 'Support Agent']
        created = 0
        for role in roles:
            group, is_new = Group.objects.get_or_create(name=role)
            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created group: {role}'))
            else:
                self.stdout.write(self.style.WARNING(f'Group already exists: {role}'))

        # Optionally, we could assign permissions here. Keep minimal for safety.
        self.stdout.write(self.style.SUCCESS(f'Done. Groups created: {created}'))
