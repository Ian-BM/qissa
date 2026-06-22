from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import ShortStory
from .services import (
    get_related_shorts,
    get_trending_shorts,
    record_short_view,
    toggle_short_like,
    user_has_liked,
)

CATEGORY_FILTERS = [
    ("", "Zote", ""),
    (ShortStory.CATEGORY_RELATIONSHIP, "Mahusiano", "❤️"),
    (ShortStory.CATEGORY_HEARTBREAK, "Huzuni", "💔"),
    (ShortStory.CATEGORY_FAMILY, "Familia", "👨‍👩‍👧"),
    (ShortStory.CATEGORY_CAMPUS, "Campus", "🎓"),
    (ShortStory.CATEGORY_INSPIRATION, "Inspiration", "🌟"),
    (ShortStory.CATEGORY_MYSTERY, "Mystery", "🔍"),
    (ShortStory.CATEGORY_LIFE_LESSONS, "Maisha", "📖"),
]


@require_http_methods(["GET"])
def short_list(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest").strip()

    shorts = ShortStory.objects.filter(published=True)

    if query:
        shorts = shorts.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(excerpt__icontains=query)
        )

    if category:
        shorts = shorts.filter(category=category)

    if sort == "trending":
        trending_ids = [s.pk for s in get_trending_shorts(limit=100)]
        if trending_ids:
            shorts = shorts.filter(pk__in=trending_ids)
            ordering = {pk: idx for idx, pk in enumerate(trending_ids)}
            shorts = sorted(shorts, key=lambda s: ordering.get(s.pk, 999))
        else:
            shorts = shorts.order_by("-created_at")
    else:
        shorts = shorts.order_by("-created_at")

    if isinstance(shorts, list):
        paginator = Paginator(shorts, 12)
    else:
        paginator = Paginator(shorts, 12)

    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "shorts/list.html",
        {
            "page_obj": page_obj,
            "shorts": page_obj,
            "query": query,
            "selected_category": category,
            "sort": sort,
            "category_filters": CATEGORY_FILTERS,
        },
    )


@require_http_methods(["GET"])
def short_detail(request, slug):
    short_story = get_object_or_404(ShortStory, slug=slug, published=True)
    record_short_view(request, short_story)

    related = get_related_shorts(short_story, limit=3)
    story_url = request.build_absolute_uri()
    share_text = f"Nimesoma simulizi hii kwenye Qissa. Isome hapa: {story_url}"

    return render(
        request,
        "shorts/detail.html",
        {
            "short": short_story,
            "related_shorts": related,
            "user_has_liked": user_has_liked(request, short_story),
            "story_url": story_url,
            "share_text": share_text,
        },
    )


@require_http_methods(["POST"])
def short_like(request, slug):
    short_story = get_object_or_404(ShortStory, slug=slug, published=True)
    toggle_short_like(request, short_story)
    return redirect("short_detail", slug=slug)
