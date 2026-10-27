from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from accounts.models import User


class Command(BaseCommand):
    help = "Expire Premium subscriptions past their end date"

    def handle(self, *args, **options):
        expired = User.objects.filter(
            Q(premium_expires_at__lte=timezone.now())
            | Q(premium_expires_at__isnull=True, premium_end__lt=timezone.now().date()),
            is_premium=True,
        )
        count = expired.count()
        expired.update(is_premium=False)
        self.stdout.write(self.style.SUCCESS(f"Expired {count} subscription(s)"))
