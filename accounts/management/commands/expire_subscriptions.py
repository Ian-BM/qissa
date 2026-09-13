from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User


class Command(BaseCommand):
    help = "Expire Premium subscriptions past their end date"

    def handle(self, *args, **options):
        expired = User.objects.filter(
            is_premium=True,
            premium_end__lt=timezone.now().date(),
        )
        count = expired.count()
        expired.update(is_premium=False)
        self.stdout.write(self.style.SUCCESS(f"Expired {count} subscription(s)"))
