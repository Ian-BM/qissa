FREE_CHAPTER_LIMIT = 4


def default_chapter_locked(order: int) -> bool:
    return order > FREE_CHAPTER_LIMIT


def chapter_requires_unlock(chapter) -> bool:
    return chapter.is_locked
