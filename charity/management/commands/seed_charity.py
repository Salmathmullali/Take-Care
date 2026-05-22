from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed placeholder for charity module (no-op; pillars use fixed constants).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Charity module ready (blood, medical-bills, food).'))
