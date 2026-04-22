from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Chapter, Story, StoryAccess

FREE_CHAPTER_LIMIT = 4


@require_http_methods(["GET"])
def story_detail(request, slug):
    story = get_object_or_404(
        Story.objects.select_related("category"),
        slug=slug,
    )

    # Chapters of the story
    chapters = story.chapters.all()
    has_story_access = (
        request.user.is_authenticated
        and StoryAccess.objects.filter(user=request.user, story=story).exists()
    )

    return render(
        request,
        "stories/story_detail.html",
        {
            "story": story,
            "chapters": chapters,
            "free_chapter_limit": FREE_CHAPTER_LIMIT,
            "has_story_access": has_story_access,
        },
    )


@login_required
@require_http_methods(["GET"])
def chapter_reader(request, id):
    chapter = get_object_or_404(
        Chapter.objects.select_related("story", "story__category"),
        id=id,
    )
    story = chapter.story

    # 🔒 LOCK CHECK
    requires_unlock = chapter.order > FREE_CHAPTER_LIMIT
    if requires_unlock:
        has_story_access = StoryAccess.objects.filter(
            user=request.user,
            
            story=story,
        ).exists()

        if not has_story_access:
            return redirect("payment_page", story_id=story.id)

        # Count a paid view only once per paid user/story.
        StoryAccess.mark_view_if_needed(user=request.user, story=story)

    prev_chapter = (
        Chapter.objects.filter(story=story, order__lt=chapter.order)
        .order_by("-order")
        .first()
    )
    next_chapter = (
        Chapter.objects.filter(story=story, order__gt=chapter.order)
        .order_by("order")
        .first()
    )
    chapters = Chapter.objects.filter(story=story).order_by("order")

    related = Story.objects.filter(
        is_published=True,
    ).exclude(id=story.id)
    if story.category_id:
        related = related.filter(category_id=story.category_id)
    related = related.order_by("-created_at")[:8]

    return render(
        request,
        "stories/chapter_reader.html",
        {
            "chapter": chapter,
            "prev_chapter": prev_chapter,
            "next_chapter": next_chapter,
            "chapters": chapters,
            "related": related,
        },
    )

@login_required
@require_http_methods(["GET"])
def payment_page(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    return render(
        request,
        "stories/payment.html",
        {
            "story": story,
            "free_chapter_limit": FREE_CHAPTER_LIMIT,
        },
    )
