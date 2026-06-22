from django.core.management.base import BaseCommand

from core.models import CleanerAction


class Command(BaseCommand):
    help = "Seed default cleaner actions"

    ACTIONS = [
        "Clean toilet bowl",
        "Clean toilet floor",
        "Refill toilet paper",
        "Refill soap dispenser",
        "Refill paper towel",
        "Clean sink",
        "Empty trash bin",
        "General cleaning",
    ]

    def handle(self, *args, **kwargs):
        count = 0
        for i, name in enumerate(self.ACTIONS):
            _, created = CleanerAction.objects.get_or_create(
                name=name, defaults={"order": i}
            )
            count += created

        self.stdout.write(self.style.SUCCESS(f"Seeded {count} cleaner actions"))
