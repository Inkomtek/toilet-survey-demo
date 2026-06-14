from django.core.management.base import BaseCommand
from core.models import Reason, Rating


class Command(BaseCommand):
    help = 'Seed default survey reasons'

    REASONS = {
        Rating.EXCELLENT: [
            "Very clean", "Pleasant smell",
            "Well stocked (tissue, soap, etc.)", "Fully functional facilities",
            "Fast staff response",
        ],
        Rating.GOOD: [
            "Clean", "Adequate supplies",
            "Facilities working well", "Comfortable environment",
        ],
        Rating.AVERAGE: [
            "Slightly dirty", "Low on supplies",
            "Minor facility issues", "Unpleasant smell",
        ],
        Rating.POOR: [
            "Dirty toilet bowl", "No tissue or soap",
            "Bad smell", "Broken facilities",
            "Wet floor", "Long queue",
        ],
    }

    def handle(self, *args, **kwargs):
        count = 0
        for rating, reasons in self.REASONS.items():
            for i, text in enumerate(reasons):
                _, created = Reason.objects.get_or_create(
                    rating=rating, text=text, defaults={'order': i}
                )
                count += created

        self.stdout.write(self.style.SUCCESS(f'Seeded {count} reasons'))
