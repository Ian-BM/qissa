from datetime import timedelta

from django.db.models import F
from django.utils import timezone

from .models import ShortStory, ShortStoryLike, ShortStoryView


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def record_short_view(request, short_story):
    """Record a unique view; increment counter only once per user/session."""
    if request.user.is_authenticated:
        _, created = ShortStoryView.objects.get_or_create(
            short_story=short_story,
            user=request.user,
        )
    else:
        _, created = ShortStoryView.objects.get_or_create(
            short_story=short_story,
            session_key=get_session_key(request),
        )

    if created:
        ShortStory.objects.filter(pk=short_story.pk).update(views=F("views") + 1)
        short_story.refresh_from_db(fields=["views"])

    return created


def user_has_liked(request, short_story):
    if request.user.is_authenticated:
        return ShortStoryLike.objects.filter(
            short_story=short_story, user=request.user
        ).exists()
    return ShortStoryLike.objects.filter(
        short_story=short_story, session_key=get_session_key(request)
    ).exists()


def toggle_short_like(request, short_story):
    """Like if not liked; returns (liked: bool, created: bool)."""
    if request.user.is_authenticated:
        like, created = ShortStoryLike.objects.get_or_create(
            short_story=short_story,
            user=request.user,
        )
        if created:
            ShortStory.objects.filter(pk=short_story.pk).update(likes=F("likes") + 1)
            short_story.refresh_from_db(fields=["likes"])
            return True, True
        return True, False

    session_key = get_session_key(request)
    like, created = ShortStoryLike.objects.get_or_create(
        short_story=short_story,
        session_key=session_key,
    )
    if created:
        ShortStory.objects.filter(pk=short_story.pk).update(likes=F("likes") + 1)
        short_story.refresh_from_db(fields=["likes"])
        return True, True
    return True, False


def get_trending_shorts(limit=5):
    """
    Trending score: views + (likes * 3) + recency boost for stories < 7 days old.
    """
    recent_cutoff = timezone.now() - timedelta(days=7)
    qs = ShortStory.objects.filter(published=True)

    scored = []
    for story in qs:
        recency_boost = 10 if story.created_at >= recent_cutoff else 0
        score = story.views + (story.likes * 3) + recency_boost
        scored.append((score, story))

    scored.sort(key=lambda item: (item[0], item[1].created_at), reverse=True)
    return [story for _, story in scored[:limit]]


def get_related_shorts(short_story, limit=3):
    related = list(
        ShortStory.objects.filter(published=True, category=short_story.category)
        .exclude(pk=short_story.pk)
        .order_by("-created_at")[:limit]
    )
    if len(related) < limit:
        needed = limit - len(related)
        exclude_ids = [short_story.pk] + [s.pk for s in related]
        related.extend(
            ShortStory.objects.filter(published=True)
            .exclude(pk__in=exclude_ids)
            .order_by("-created_at")[:needed]
        )
    return related
