from decimal import Decimal

from .models import Purchase, StoryAccess


def record_purchase(user, story, payment_reference=""):
    """Record an immutable purchase when a reader gains story access."""
    if Purchase.objects.filter(reader=user, story=story).exists():
        return None

    amount = story.price or Decimal("0")
    return Purchase.objects.create(
        reader=user,
        story=story,
        amount_paid=amount,
        payment_reference=payment_reference or f"access-{user.id}-{story.id}",
    )


def grant_story_access(user, story, payment_reference=""):
    """Grant story access and record purchase if newly granted."""
    access, created = StoryAccess.objects.get_or_create(user=user, story=story)
    if created:
        StoryAccess.mark_view_if_needed(user=user, story=story)
        record_purchase(user, story, payment_reference=payment_reference)
    return access, created
