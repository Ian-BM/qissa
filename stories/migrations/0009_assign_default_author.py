from decimal import Decimal

from django.db import migrations


def assign_default_author_and_backfill(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Author = apps.get_model("accounts", "Author")
    Story = apps.get_model("stories", "Story")
    StoryAccess = apps.get_model("stories", "StoryAccess")
    Purchase = apps.get_model("stories", "Purchase")
    WriterEarning = apps.get_model("stories", "WriterEarning")

    user = User.objects.filter(is_staff=True).order_by("id").first()
    if not user:
        user = User.objects.order_by("id").first()
    if not user:
        return

    author, _ = Author.objects.get_or_create(
        user=user,
        defaults={
            "pen_name": "Qissa",
            "slug": "qissa",
            "bio": "Official Qissa stories",
            "approved": True,
        },
    )

    Story.objects.filter(author__isnull=True).update(author=author)

    writer_ratio = Decimal("0.70")
    qissa_ratio = Decimal("0.30")

    for access in StoryAccess.objects.select_related("story", "user").iterator():
        story = access.story
        if Purchase.objects.filter(reader=access.user, story=story).exists():
            continue

        amount = story.price or Decimal("0")
        purchase = Purchase.objects.create(
            reader=access.user,
            story=story,
            amount_paid=amount,
            payment_reference=f"backfill-{access.id}",
            purchased_at=access.granted_at,
        )

        if story.author_id and amount > 0:
            writer_share = (amount * writer_ratio).quantize(Decimal("0.01"))
            qissa_share = (amount * qissa_ratio).quantize(Decimal("0.01"))
            WriterEarning.objects.create(
                author_id=story.author_id,
                purchase=purchase,
                story=story,
                gross_amount=amount,
                writer_share=writer_share,
                qissa_share=qissa_share,
                created_at=access.granted_at,
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_authorapplication_author"),
        ("stories", "0008_purchase_story_author_writerearning_purchase_story_and_more"),
    ]

    operations = [
        migrations.RunPython(assign_default_author_and_backfill, noop_reverse),
    ]
