from datetime import date, datetime

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, F, Max, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import User
from core.utils import admin_required
from dashboard.analytics import (
    get_category_performance,
    get_platform_stats,
    get_premium_stats,
    get_reader_growth,
    get_revenue_trend,
    get_story_leaderboards,
    get_story_monetization,
    get_story_performance_chart,
)
from shorts.forms import ShortStoryForm
from shorts.models import ShortStory
from stories.forms import ChapterForm, StoryForm
from stories.locking import default_chapter_locked
from stories.models import Chapter, Story, StoryAccess, StoryReaction
from stories.services import grant_story_access


def _staff_check(request):
    if not request.user.is_staff:
        return redirect("/")
    return None


@admin_required
def dashboard_home(request):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp

    stats = get_platform_stats()
    leaders = get_story_leaderboards()
    revenue_trend = get_revenue_trend()
    reader_growth = get_reader_growth()
    category_perf = get_category_performance()
    story_perf = get_story_performance_chart()
    premium_stats = get_premium_stats()

    return render(
        request,
        "dash/home.html",
        {
            "stats": stats,
            "leaders": leaders,
            "revenue_trend": revenue_trend,
            "reader_growth": reader_growth,
            "category_perf": category_perf,
            "story_perf": story_perf,
            "premium_stats": premium_stats,
        },
    )


@admin_required
def story_list(request):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp

    stories = (
        Story.objects.annotate(
            likes_count=Count("reactions", filter=Q(reactions__value=StoryReaction.LIKE)),
            sales_count=Count("purchases", distinct=True),
            revenue=Sum("purchases__amount_paid"),
            chapter_count=Count("chapters"),
        )
        .select_related("category")
        .order_by("-created_at")
    )
    return render(request, "dash/story_list.html", {"stories": stories})


@admin_required
def story_create(request):
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save()
            messages.success(request, "Story created. Add chapters below.")
            return redirect("story_manage", story_id=story.id)
    else:
        form = StoryForm()
    return render(request, "dash/story_form.html", {"form": form, "mode": "create"})


@admin_required
def story_edit(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            messages.success(request, "Story updated.")
            return redirect("story_manage", story_id=story.id)
    else:
        form = StoryForm(instance=story)
    monetization = get_story_monetization(story)
    return render(
        request,
        "dash/story_form.html",
        {"form": form, "mode": "edit", "story": story, "monetization": monetization},
    )


@admin_required
def story_manage(request, story_id):
    story = get_object_or_404(
        Story.objects.annotate(
            chapter_count=Count("chapters"),
            last_chapter_at=Max("chapters__created_at"),
        ),
        id=story_id,
    )
    monetization = get_story_monetization(story)
    chapters = story.chapters.order_by("order")
    last_updated = story.last_chapter_at or story.updated_at or story.created_at
    return render(
        request,
        "dash/story_manage.html",
        {
            "story": story,
            "monetization": monetization,
            "chapters": chapters,
            "last_updated": last_updated,
        },
    )


@admin_required
def story_update_price(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.method == "POST":
        price = request.POST.get("price", "0").strip()
        try:
            story.price = max(float(price), 0)
            story.save(update_fields=["price"])
            messages.success(request, f"Price updated to TZS {story.price:,.0f}.")
        except ValueError:
            messages.error(request, "Enter a valid price.")
    return redirect("story_manage", story_id=story.id)


@admin_required
@require_http_methods(["POST"])
def story_toggle_publish(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    story.is_published = not story.is_published
    story.save(update_fields=["is_published"])
    if story.is_published:
        messages.success(request, f'"{story.title}" is now published.')
    else:
        messages.info(request, f'"{story.title}" moved to drafts.')
    return redirect("story_list")


@admin_required
@require_http_methods(["POST"])
def story_delete(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    title = story.title
    story.delete()
    messages.success(request, f'"{title}" deleted.')
    return redirect("story_list")


@admin_required
def chapter_list(request, story_id):
    return redirect("story_manage", story_id=story_id)


@admin_required
def chapter_create(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.story = story
            if "is_locked" not in request.POST:
                chapter.is_locked = default_chapter_locked(chapter.order)
            chapter.save()
            story.save(update_fields=["updated_at"])
            messages.success(request, "Chapter created.")
            return redirect("story_manage", story_id=story.id)
    else:
        next_order = story.chapters.aggregate(Max("order"))["order__max"] or 0
        form = ChapterForm(initial={"order": next_order + 1})
    return render(
        request,
        "dash/chapter_form.html",
        {"form": form, "story": story, "mode": "create"},
    )


@admin_required
def chapter_edit(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    if request.method == "POST":
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            chapter.story.save(update_fields=["updated_at"])
            messages.success(request, "Chapter updated.")
            return redirect("story_manage", story_id=chapter.story.id)
    else:
        form = ChapterForm(instance=chapter)
    return render(
        request,
        "dash/chapter_form.html",
        {"form": form, "story": chapter.story, "mode": "edit", "chapter": chapter},
    )


@admin_required
@require_http_methods(["POST"])
def chapter_toggle_lock(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    chapter.is_locked = not chapter.is_locked
    chapter.save(update_fields=["is_locked"])
    state = "locked" if chapter.is_locked else "unlocked"
    messages.success(request, f"Chapter {chapter.order} is now {state}.")
    return redirect("story_manage", story_id=chapter.story.id)


@admin_required
@require_http_methods(["POST"])
def chapter_bulk_lock(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    chapter_ids = request.POST.getlist("chapter_ids")
    action = request.POST.get("action")
    if not chapter_ids or action not in {"lock", "unlock"}:
        messages.error(request, "Select chapters and an action.")
        return redirect("story_manage", story_id=story.id)

    lock_value = action == "lock"
    updated = Chapter.objects.filter(story=story, id__in=chapter_ids).update(
        is_locked=lock_value
    )
    messages.success(request, f"Updated {updated} chapter(s).")
    return redirect("story_manage", story_id=story.id)


@admin_required
@require_http_methods(["POST"])
def chapter_delete(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    story = chapter.story
    title = chapter.title
    order = chapter.order
    chapter.delete()
    Chapter.objects.filter(story=story, order__gt=order).update(order=F("order") - 1)
    story.save(update_fields=["updated_at"])
    messages.success(request, f'Deleted chapter "{title}".')
    return redirect("story_manage", story_id=story.id)


@admin_required
@require_http_methods(["POST"])
def chapter_reorder(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    direction = request.POST.get("direction")
    story = chapter.story

    if direction == "up":
        neighbor = (
            Chapter.objects.filter(story=story, order__lt=chapter.order)
            .order_by("-order")
            .first()
        )
    elif direction == "down":
        neighbor = (
            Chapter.objects.filter(story=story, order__gt=chapter.order)
            .order_by("order")
            .first()
        )
    else:
        messages.error(request, "Invalid reorder action.")
        return redirect("story_manage", story_id=story.id)

    if not neighbor:
        messages.info(request, "Chapter is already at the boundary.")
        return redirect("story_manage", story_id=story.id)

    with transaction.atomic():
        temp_order = (story.chapters.aggregate(Max("order"))["order__max"] or 0) + 1000
        Chapter.objects.filter(pk=chapter.pk).update(order=temp_order)
        Chapter.objects.filter(pk=neighbor.pk).update(order=chapter.order)
        Chapter.objects.filter(pk=chapter.pk).update(order=neighbor.order)

    story.save(update_fields=["updated_at"])
    messages.success(request, "Chapter order updated.")
    return redirect("story_manage", story_id=story.id)


@admin_required
def monetization_overview(request):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp
    leaders = get_story_leaderboards()
    stories = (
        Story.objects.annotate(
            sales_count=Count("purchases", distinct=True),
            revenue=Sum("purchases__amount_paid"),
        )
        .order_by("-revenue")
    )
    return render(
        request,
        "dash/monetization.html",
        {"top_earning": leaders["top_earning_stories"], "stories": stories},
    )


@admin_required
def performance_overview(request):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp
    return render(
        request,
        "dash/performance.html",
        {
            "story_perf": get_story_performance_chart(),
            "category_perf": get_category_performance(),
            "leaders": get_story_leaderboards(),
        },
    )


@admin_required
def shorts_overview(request):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp
    shorts = ShortStory.objects.all().order_by("-created_at")
    return render(request, "dash/shorts.html", {"shorts": shorts})


@admin_required
def short_create(request):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp
    if request.method == "POST":
        form = ShortStoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Short story created.")
            return redirect("dashboard_shorts")
    else:
        form = ShortStoryForm()
    return render(request, "dash/short_form.html", {"form": form, "mode": "create"})


@admin_required
def short_edit(request, short_id):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp
    short = get_object_or_404(ShortStory, id=short_id)
    if request.method == "POST":
        form = ShortStoryForm(request.POST, request.FILES, instance=short)
        if form.is_valid():
            form.save()
            messages.success(request, "Short story updated.")
            return redirect("dashboard_shorts")
    else:
        form = ShortStoryForm(instance=short)
    return render(
        request,
        "dash/short_form.html",
        {"form": form, "mode": "edit", "short": short},
    )


@admin_required
@require_http_methods(["POST"])
def short_toggle_publish(request, short_id):
    short = get_object_or_404(ShortStory, id=short_id)
    short.published = not short.published
    short.save(update_fields=["published"])
    state = "published" if short.published else "draft"
    messages.success(request, f'"{short.title}" is now a {state}.')
    return redirect("dashboard_shorts")


@admin_required
@require_http_methods(["POST"])
def short_delete(request, short_id):
    short = get_object_or_404(ShortStory, id=short_id)
    title = short.title
    short.delete()
    messages.success(request, f'"{title}" deleted.')
    return redirect("dashboard_shorts")


@admin_required
def drafts_overview(request):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp
    stories = Story.objects.filter(is_published=False).order_by("-created_at")
    return render(request, "dash/drafts.html", {"stories": stories})


@admin_required
def unlock_chapter(request):
    story_id = request.GET.get("story")
    selected_story = Story.objects.filter(id=story_id).first() if story_id else None
    users = User.objects.all().order_by("name", "phone")
    story_access_map = set()
    if selected_story:
        story_access_map = set(
            StoryAccess.objects.filter(story=selected_story).values_list(
                "user_id", flat=True
            )
        )
    return render(
        request,
        "dash/unlock.html",
        {
            "stories": Story.objects.all().order_by("title"),
            "selected_story": selected_story,
            "users": users,
            "story_access_map": story_access_map,
        },
    )


@admin_required
def premium_activate(request):
    redirect_resp = _staff_check(request)
    if redirect_resp:
        return redirect_resp

    search_phone = request.GET.get("phone", "").strip()
    found_user = None
    if search_phone:
        found_user = User.objects.filter(phone__icontains=search_phone).first()

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        end_date_raw = request.POST.get("end_date", "").strip()
        target_user = get_object_or_404(User, id=user_id)
        try:
            end_date = datetime.strptime(end_date_raw, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Chagua tarehe sahihi ya mwisho.")
            return redirect(f"/dashboard/premium/?phone={target_user.phone}")

        target_user.is_premium = True
        target_user.premium_start = date.today()
        target_user.premium_end = end_date
        target_user.save(update_fields=["is_premium", "premium_start", "premium_end"])
        messages.success(
            request, f"Premium imewashwa kwa {target_user.name or target_user.phone}."
        )
        return redirect(f"/dashboard/premium/?phone={target_user.phone}")

    recent_activations = User.objects.filter(is_premium=True).order_by(
        "-premium_start"
    )[:10]

    return render(
        request,
        "dash/premium.html",
        {
            "search_phone": search_phone,
            "found_user": found_user,
            "recent_activations": recent_activations,
        },
    )


@admin_required
def premium_deactivate(request, user_id):
    if request.method != "POST":
        return redirect("premium_activate")
    target_user = get_object_or_404(User, id=user_id)
    target_user.is_premium = False
    target_user.save(update_fields=["is_premium"])
    messages.info(request, f"Premium imezimwa kwa {target_user.name or target_user.phone}.")
    return redirect(f"/dashboard/premium/?phone={target_user.phone}")


@admin_required
def toggle_story_access(request, story_id, user_id):
    if request.method != "POST":
        return redirect("unlock_chapter")
    story = get_object_or_404(Story, id=story_id)
    user = get_object_or_404(User, id=user_id)
    if StoryAccess.objects.filter(user=user, story=story).exists():
        StoryAccess.objects.filter(user=user, story=story).delete()
        messages.info(request, f"Deactivated {user.phone} for {story.title}.")
    else:
        grant_story_access(
            user,
            story,
            payment_reference=f"manual-unlock-{user.id}-{story.id}",
        )
        messages.success(request, f"Activated {user.phone} for {story.title}.")
    return redirect(f"/dashboard/unlock/?story={story.id}")
