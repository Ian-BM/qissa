from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator

from stories.models import Story, StoryCategory


def home(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    stories = Story.objects.filter(
        is_published=True
    ).select_related("category").order_by("-created_at")

    if query:
        stories = stories.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(chapters__title__icontains=query) |
            Q(chapters__content__icontains=query)
        ).distinct()

    if category_slug:
        stories = stories.filter(category__slug=category_slug)

    categories = StoryCategory.objects.filter(stories__is_published=True).distinct()

    paginator = Paginator(stories, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "pages/home.html", {
        "stories": page_obj,
        "page_obj": page_obj,
        "query": query,
        "categories": categories,
        "selected_category_slug": category_slug,
    })
