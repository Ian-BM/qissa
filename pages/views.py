from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator

from stories.models import Story


def home(request):
    query = request.GET.get("q", "").strip()

    stories = Story.objects.filter(
        is_published=True
    ).order_by("-created_at")

    if query:
        stories = stories.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(chapters__title__icontains=query) |
            Q(chapters__content__icontains=query)
        ).distinct()

    paginator = Paginator(stories, 30)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "pages/home.html", {
        "stories": page_obj,
        "page_obj": page_obj,
        "query": query,
    })
