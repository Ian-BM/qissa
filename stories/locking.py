FREE_CHAPTER_LIMIT = 4


def default_chapter_locked(order: int) -> bool:
    return order > FREE_CHAPTER_LIMIT


def chapter_requires_unlock(chapter) -> bool:
    return chapter.is_locked


def user_has_chapter_access(user, chapter) -> bool:
    """A locked chapter is readable with an active Premium subscription,
    or a manual per-story grant made by an admin (StoryAccess)."""
    if not chapter.is_locked:
        return True
    if not user.is_authenticated:
        return False
    if user.is_subscription_active():
        return True
    from .models import StoryAccess

    return StoryAccess.objects.filter(user=user, story_id=chapter.story_id).exists()
