from django.db.models import F

from .models import Chapter, ChapterRead, Story


def record_chapter_read(*, user, chapter: Chapter) -> None:
    Chapter.objects.filter(pk=chapter.pk).update(views=F("views") + 1)
    ChapterRead.objects.get_or_create(user=user, chapter=chapter)


def record_locked_chapter_click(*, story: Story) -> None:
    Story.objects.filter(pk=story.pk).update(
        locked_chapter_clicks=F("locked_chapter_clicks") + 1
    )


def record_purchase_attempt(*, story: Story) -> None:
    Story.objects.filter(pk=story.pk).update(
        purchase_attempts=F("purchase_attempts") + 1
    )
