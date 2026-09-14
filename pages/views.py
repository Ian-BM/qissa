from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render

from shorts.models import ShortStory
from stories.models import Story, StoryCategory, StoryReaction


def _published_stories():
    return (
        Story.objects.filter(is_published=True)
        .select_related("category", "author")
        .annotate(
            likes_count=Count(
                "reactions", filter=Q(reactions__value=StoryReaction.LIKE)
            ),
            chapter_count=Count("chapters", distinct=True),
        )
    )


GENRE_SLUGS = {"mapenzi", "drama", "kusisimua", "mzimu", "kampasi"}


def home(request):
    current_filter = request.GET.get("filter", "mpya").strip()

    stories = _published_stories()

    if current_filter == "maarufu":
        stories = stories.order_by("-views")
    elif current_filter in GENRE_SLUGS:
        stories = stories.filter(category__slug=current_filter).order_by("-created_at")
    else:
        current_filter = "mpya"
        stories = stories.order_by("-created_at")

    featured = (
        _published_stories()
        .filter(is_featured=True)
        .order_by("-created_at")
        .first()
    )

    paginator = Paginator(stories, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    latest_shorts = ShortStory.objects.filter(published=True).order_by("-created_at")[:12]

    return render(
        request,
        "pages/home.html",
        {
            "featured": featured,
            "stories": page_obj,
            "current_filter": current_filter,
            "latest_shorts": latest_shorts,
        },
    )


def premium(request):
    return render(request, "payment/premium.html")


def stories_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    stories = _published_stories().order_by("-updated_at", "-created_at")

    if query:
        stories = stories.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(author__pen_name__icontains=query)
        ).distinct()

    if category_slug:
        stories = stories.filter(category__slug=category_slug)

    paginator = Paginator(stories, 24)
    page_obj = paginator.get_page(request.GET.get("page"))
    categories = StoryCategory.objects.filter(stories__is_published=True).distinct()

    return render(
        request,
        "pages/stories_list.html",
        {
            "stories": page_obj,
            "page_obj": page_obj,
            "query": query,
            "categories": categories,
            "selected_category_slug": category_slug,
        },
    )
