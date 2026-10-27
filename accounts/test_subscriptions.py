from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import PremiumActivation, User
from accounts.subscriptions import PLANS, activate_verified_subscription, get_plan
from stories.locking import user_has_chapter_access
from stories.models import Chapter, Story


class PremiumPlanTests(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user("+255712345678", "Reader")
        self.staff = User.objects.create_user("+255713345678", "Staff")
        self.staff.is_staff = True
        self.staff.save(update_fields=["is_staff"])
        self.now = timezone.now()

    def activate(self, plan="daily", reference="PAYMENT-1"):
        return activate_verified_subscription(
            user_id=self.reader.pk, plan_id=plan,
            payment_reference=reference, verified_by=self.staff)

    def test_all_plan_prices_and_exact_durations(self):
        self.assertEqual(len(PLANS), 3)
        for plan_id, amount, days in [("daily", 1000, 1), ("weekly", 3000, 7), ("monthly", 7000, 30)]:
            with self.subTest(plan=plan_id), patch("accounts.subscriptions.timezone.now", return_value=self.now):
                self.reader.is_premium = False
                self.reader.save(update_fields=["is_premium"])
                activation = self.activate(plan_id, plan_id)
                self.assertEqual(get_plan(plan_id).amount, amount)
                self.assertEqual(activation.amount, amount)
                self.assertEqual(activation.activated_at, self.now)
                self.assertEqual(activation.expires_at, self.now + timedelta(days=days))
                self.assertTrue(timezone.is_aware(activation.expires_at))
                self.reader.refresh_from_db()
                self.assertEqual(self.reader.subscription_expires_at(), activation.expires_at)

    def test_access_expires_at_exact_timestamp(self):
        activation = self.activate()
        self.reader.refresh_from_db()
        with patch("django.utils.timezone.now", return_value=activation.expires_at - timedelta(microseconds=1)):
            self.assertTrue(self.reader.is_subscription_active())
        with patch("django.utils.timezone.now", return_value=activation.expires_at):
            self.assertFalse(self.reader.is_subscription_active())

    def test_legacy_subscription_preserves_entire_end_date(self):
        self.reader.is_premium = True
        self.reader.premium_end = self.now.date() + timedelta(days=20)
        self.reader.save()
        expiry = self.reader.subscription_expires_at()
        with patch("django.utils.timezone.now", return_value=expiry - timedelta(microseconds=1)):
            self.assertTrue(self.reader.is_subscription_active())
        with patch("django.utils.timezone.now", return_value=expiry):
            self.assertFalse(self.reader.is_subscription_active())
        end = self.reader.premium_end
        activation = self.activate()
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.premium_end, end)
        self.assertEqual(activation.activated_at, expiry)
        self.assertEqual(activation.expires_at, expiry + timedelta(days=1))

    def test_renewal_extends_existing_timestamp(self):
        first = self.activate()
        second = self.activate("weekly", "PAYMENT-2")
        self.assertEqual(second.activated_at, first.expires_at)
        self.assertEqual(second.expires_at, first.expires_at + timedelta(days=7))

    def test_duplicate_reference_does_not_extend_twice(self):
        first = self.activate(reference=" abc123 ")
        repeated = self.activate(reference="ABC123")
        self.assertEqual(first.pk, repeated.pk)
        self.assertEqual(PremiumActivation.objects.count(), 1)
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.premium_expires_at, first.expires_at)

    def test_reused_reference_with_different_plan_is_rejected(self):
        self.activate()
        with self.assertRaises(ValueError):
            self.activate("monthly")

    def test_reused_reference_with_different_reader_is_rejected(self):
        self.activate()
        other = User.objects.create_user("+255714345678", "Other")
        with self.assertRaises(ValueError):
            activate_verified_subscription(user_id=other.pk, plan_id="daily",
                                           payment_reference="PAYMENT-1", verified_by=self.staff)

    def test_invalid_plan_or_missing_reference_is_rejected(self):
        for plan, reference in [("invalid", "PAYMENT"), ("daily", " "), ("daily", "A" * 101)]:
            with self.subTest(plan=plan), self.assertRaises(ValueError):
                self.activate(plan, reference)
        self.assertFalse(PremiumActivation.objects.exists())

    def test_nonstaff_cannot_verify_payment(self):
        with self.assertRaises(ValueError):
            activate_verified_subscription(user_id=self.reader.pk, plan_id="daily",
                                           payment_reference="PAYMENT", verified_by=self.reader)

    def test_pricing_selection_never_activates_or_trusts_browser_amount(self):
        self.client.force_login(self.reader)
        for plan in PLANS:
            response = self.client.get(reverse("premium"), {"plan": plan.id, "amount": 1})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "TZS " + plan.price)
            self.assertEqual(response.context["selected_plan"].amount, plan.amount)
        self.assertFalse(PremiumActivation.objects.exists())
        self.reader.refresh_from_db()
        self.assertFalse(self.reader.is_premium)
        self.assertEqual(self.client.get(reverse("premium"), {"plan": "fake"}).status_code, 400)

    def test_staff_activation_uses_server_price_and_requires_confirmation(self):
        self.client.force_login(self.staff)
        data = {"user_id": self.reader.pk, "plan": "weekly", "payment_reference": "VERIFIED", "amount": 1}
        self.client.post(reverse("premium_activate"), data)
        self.assertFalse(PremiumActivation.objects.exists())
        data["payment_verified"] = "yes"
        self.client.post(reverse("premium_activate"), data)
        self.assertEqual(PremiumActivation.objects.get().amount, 3000)
        self.client.post(reverse("premium_activate"), data)
        self.assertEqual(PremiumActivation.objects.count(), 1)

    def test_reader_cannot_activate_from_dashboard(self):
        self.client.force_login(self.reader)
        response = self.client.post(reverse("premium_activate"), {
            "user_id": self.reader.pk, "plan": "monthly", "payment_reference": "UNVERIFIED", "payment_verified": "yes"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(PremiumActivation.objects.exists())

    def test_locked_content_uses_precise_expiry_for_every_plan(self):
        story = Story.objects.create(title="Premium", description="Test", is_published=True)
        chapter = Chapter.objects.create(story=story, title="Locked", content="Text", order=5, is_locked=True)
        for plan in PLANS:
            with self.subTest(plan=plan.id):
                activation = self.activate(plan.id, plan.id)
                self.reader.refresh_from_db()
                self.assertTrue(user_has_chapter_access(self.reader, chapter))
                with patch("django.utils.timezone.now", return_value=activation.expires_at):
                    self.assertFalse(user_has_chapter_access(self.reader, chapter))

    def test_expiry_command_respects_timestamps_and_legacy_dates(self):
        activation = self.activate()
        self.reader.refresh_from_db()
        self.staff.is_premium = True
        self.staff.premium_end = activation.expires_at.date() + timedelta(days=7)
        self.staff.save()
        with patch("django.utils.timezone.now", return_value=activation.expires_at):
            call_command("expire_subscriptions", verbosity=0)
        self.reader.refresh_from_db()
        self.staff.refresh_from_db()
        self.assertFalse(self.reader.is_premium)
        self.assertTrue(self.staff.is_premium)
