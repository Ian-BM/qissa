from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import Chapter, Story, StoryAccess


FREE_CHAPTER_LIMIT = 4


@require_http_methods(["GET"])
def story_detail(request, slug):
    story = get_object_or_404(Story, slug=slug)

    Story.objects.filter(id=story.id).update(views=F("views") + 1)
    story.refresh_from_db(fields=["views"])

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
    chapter = get_object_or_404(Chapter, id=id)
    story = chapter.story

    requires_unlock = chapter.order > FREE_CHAPTER_LIMIT
    if requires_unlock:
        has_story_access = StoryAccess.objects.filter(
            user=request.user,
            story=story,
        ).exists()
        if not has_story_access:
            return redirect("payment_page", story_id=story.id)

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

    return render(
        request,
        "stories/chapter_reader.html",
        {
            "chapter": chapter,
            "prev_chapter": prev_chapter,
            "next_chapter": next_chapter,
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
