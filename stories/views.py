from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.db.models import F

from .models import Story, Chapter


@require_http_methods(["GET"])
def story_detail(request, slug):
    story = get_object_or_404(Story, slug=slug)

    # Atomic view increment (safe for concurrency)
    Story.objects.filter(id=story.id).update(views=F("views") + 1)
    story.refresh_from_db(fields=["views"])

    # Chapters of the story
    chapters = story.chapters.all()

    return render(request, "stories/story_detail.html", {
        "story": story,
        "chapters": chapters,
    })


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import Chapter
from .models import ChapterAccess


@login_required
@require_http_methods(["GET"])
def chapter_reader(request, id):
    chapter = get_object_or_404(Chapter, id=id)
    story = chapter.story

    # 🔒 LOCK CHECK
    if chapter.is_locked:
        has_access = ChapterAccess.objects.filter(
            user=request.user,
            chapter=chapter
        ).exists()

        if not has_access:
            return redirect("payment_page", chapter_id=chapter.id)

    # ⬅️➡️ PREV / NEXT NAVIGATION
    prev_chapter = Chapter.objects.filter(
        story=story,
        order__lt=chapter.order
    ).order_by("-order").first()

    next_chapter = Chapter.objects.filter(
        story=story,
        order__gt=chapter.order
    ).order_by("order").first()

    return render(request, "stories/chapter_reader.html", {
        "chapter": chapter,
        "prev_chapter": prev_chapter,
        "next_chapter": next_chapter,
    })

@login_required
def payment_page(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)

    return render(request, "stories/payment.html", {
        "chapter": chapter,
    })

