from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate

from shorts.models import ShortStory
from stories.models import ChapterRead, Purchase, Story, StoryCategory, StoryReaction


def get_platform_stats():
    stories = Story.objects.all()
    shorts = ShortStory.objects.filter(published=True)
    purchases = Purchase.objects.all()

    total_revenue = purchases.aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")
    story_views = stories.aggregate(total=Sum("views"))["total"] or 0
    short_views = shorts.aggregate(total=Sum("views"))["total"] or 0

    return {
        "total_stories": stories.filter(is_published=True).count(),
        "total_shorts": shorts.count(),
        "total_views": story_views + short_views,
        "total_revenue": total_revenue,
        "total_purchases": purchases.count(),
        "draft_stories": stories.filter(is_published=False).count(),
    }


def _annotated_stories():
    return Story.objects.annotate(
        sales_count=Count("purchases", distinct=True),
        revenue=Sum("purchases__amount_paid"),
        likes_count=Count("reactions", filter=Q(reactions__value=StoryReaction.LIKE)),
    ).select_related("category")


def get_story_leaderboards():
    stories = _annotated_stories().filter(is_published=True)
    best_views = stories.order_by("-views").first()
    best_revenue = stories.order_by("-revenue").first()
    fastest_growing = stories.order_by("-created_at").first()
    top_earning = list(stories.filter(revenue__gt=0).order_by("-revenue")[:10])
    best_short = ShortStory.objects.filter(published=True).order_by("-views").first()

    return {
        "best_views_story": best_views,
        "best_revenue_story": best_revenue,
        "fastest_growing_story": fastest_growing,
        "best_short": best_short,
        "top_earning_stories": top_earning,
    }


def get_revenue_trend(days=14):
    return list(
        Purchase.objects.annotate(day=TruncDate("purchased_at"))
        .values("day")
        .annotate(total=Sum("amount_paid"), count=Count("id"))
        .order_by("-day")[:days]
    )[::-1]


def get_reader_growth(days=14):
    rows = list(
        Purchase.objects.annotate(day=TruncDate("purchased_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("-day")[:days]
    )
    return rows[::-1]


def get_category_performance():
    return list(
        StoryCategory.objects.annotate(
            story_count=Count("stories"),
            total_views=Sum("stories__views"),
        )
        .order_by("-total_views")[:8]
    )


def get_story_performance_chart():
    return list(
        _annotated_stories()
        .filter(is_published=True)
        .order_by("-views")[:8]
        .values("title", "views", "sales_count")
    )


def get_story_monetization(story: Story) -> dict:
    chapters = story.chapters.order_by("order")
    locked_count = chapters.filter(is_locked=True).count()
    unlocked_count = chapters.count() - locked_count
    purchase_count = story.purchases.count()
    revenue = story.purchases.aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")
    locked_clicks = story.locked_chapter_clicks or 0
    conversion = (
        round((purchase_count / locked_clicks) * 100, 1) if locked_clicks else 0
    )

    chapter_stats = []
    prev_views = None
    for chapter in chapters:
        unique_readers = ChapterRead.objects.filter(chapter=chapter).count()
        drop_off = None
        if prev_views and prev_views > 0:
            drop_off = round(((prev_views - chapter.views) / prev_views) * 100, 1)
        chapter_stats.append(
            {
                "chapter": chapter,
                "unique_readers": unique_readers,
                "drop_off_rate": drop_off,
            }
        )
        prev_views = chapter.views

    return {
        "locked_count": locked_count,
        "unlocked_count": unlocked_count,
        "purchase_count": purchase_count,
        "revenue": revenue,
        "conversion_rate": conversion,
        "locked_clicks": locked_clicks,
        "purchase_attempts": story.purchase_attempts or 0,
        "chapter_stats": chapter_stats,
        "projected_revenue": story.price * max(locked_clicks - purchase_count, 0),
    }
