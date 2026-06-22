from django.db.models import Count, Q
from django.shortcuts import render

from accounts.models import User
from shorts.models import ShortStory
from shorts.services import get_trending_shorts
from stories.models import Story, StoryCategory, StoryReaction


def home(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    base_stories = Story.objects.filter(is_published=True).select_related("category", "author")

    stories = base_stories.annotate(
        likes_count=Count("reactions", filter=Q(reactions__value=StoryReaction.LIKE))
    ).order_by("-created_at")

    if query:
        stories = stories.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(chapters__title__icontains=query)
            | Q(chapters__content__icontains=query)
        ).distinct()

    if category_slug:
        stories = stories.filter(category__slug=category_slug)

    from django.core.paginator import Paginator

    paginator = Paginator(stories, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    trending_stories = (
        base_stories.annotate(
            likes_count=Count(
                "reactions", filter=Q(reactions__value=StoryReaction.LIKE)
            )
        )
        .order_by("-views", "-likes_count")[:8]
    )

    new_releases = (
        base_stories.annotate(
            likes_count=Count(
                "reactions", filter=Q(reactions__value=StoryReaction.LIKE)
            )
        )
        .order_by("-created_at")[:8]
    )

    categories = StoryCategory.objects.filter(stories__is_published=True).distinct()

    stats = {
        "stories_count": Story.objects.filter(is_published=True).count(),
        "readers_count": User.objects.filter(is_active=True).count(),
        "categories_count": categories.count(),
    }

    latest_shorts = ShortStory.objects.filter(published=True).order_by("-created_at")[:6]
    trending_shorts = get_trending_shorts(limit=5)

    return render(
        request,
        "pages/home.html",
        {
            "stories": page_obj,
            "page_obj": page_obj,
            "query": query,
            "categories": categories,
            "selected_category_slug": category_slug,
            "trending_stories": trending_stories,
            "new_releases": new_releases,
            "stats": stats,
            "latest_shorts": latest_shorts,
            "trending_shorts": trending_shorts,
        },
    )
