"""Server-owned Premium pricing and manual payment verification."""
from dataclasses import dataclass
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from .models import PremiumActivation, User


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    amount: int
    days: int
    duration: str

    @property
    def price(self):
        return f"{self.amount:,}"


PLANS = (
    Plan("daily", "Kila Siku", 1000, 1, "Saa 24"),
    Plan("weekly", "Kila Wiki", 3000, 7, "Siku 7"),
    Plan("monthly", "Kila Mwezi", 7000, 30, "Siku 30"),
)


def get_plan(plan_id):
    for plan in PLANS:
        if plan.id == plan_id:
            return plan
    raise ValueError("Chagua mpango sahihi wa Premium.")


@transaction.atomic
def activate_verified_subscription(*, user_id, plan_id, payment_reference, verified_by):
    if not verified_by.is_active or not verified_by.is_staff:
        raise ValueError("Staff verification is required.")
    plan = get_plan(plan_id)
    reference = payment_reference.strip().upper()
    if not reference or len(reference) > 100:
        raise ValueError("Weka kumbukumbu sahihi ya malipo yaliyothibitishwa.")
    user = User.objects.select_for_update().get(pk=user_id)
    now = timezone.now()
    # Renewals queue after existing access; never shorten a purchased period.
    start = max(now, user.subscription_expires_at()) if user.is_subscription_active() else now
    expiry = start + timedelta(days=plan.days)
    activation, created = PremiumActivation.objects.get_or_create(
        payment_reference=reference,
        defaults=dict(user=user, plan=plan.id, amount=plan.amount,
                      activated_at=start, expires_at=expiry, verified_by=verified_by),
    )
    if not created:
        if activation.user_id != user.pk or activation.plan != plan.id:
            raise ValueError("Kumbukumbu hii ya malipo imetumika tayari.")
        return activation
    user.is_premium = True
    user.premium_activated_at = start
    user.premium_expires_at = expiry
    user.save(update_fields=["is_premium", "premium_activated_at", "premium_expires_at"])
    return activation
