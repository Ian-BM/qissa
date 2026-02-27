from django.shortcuts import render, redirect, get_object_or_404
from stories.models import Story
from stories.forms import StoryForm
from core.utils import admin_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from core.utils import admin_required
from stories.forms import ChapterForm, StoryForm
from stories.models import Chapter, Story, StoryAccess


@admin_required
def dashboard_home(request):
    if not request.user.is_staff:
        return redirect('/')
    
    stories = Story.objects.all().order_by("-created_at")
    return render(
        request,
        "dash/home.html",
        {
            "stories": stories,
        },
    )


@admin_required
def story_create(request):
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("dashboard_home")
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
            return redirect("dashboard_home")
    else:
        form = StoryForm(instance=story)

    return render(
        request,
        "dash/story_form.html",
        {
            "form": form,
            "mode": "edit",
            "story": story,
        },
    )


@admin_required
def story_toggle_publish(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    story.is_published = not story.is_published
    story.save(update_fields=["is_published"])
    return redirect("dashboard_home")




@admin_required
def chapter_list(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    chapters = story.chapters.all()

    return render(
        request,
        "dash/chapter_list.html",
        {
            "story": story,
            "chapters": chapters,
        },
    )


@admin_required
def chapter_create(request, story_id):

    story = get_object_or_404(Story, id=story_id)

    if request.method == "POST":
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.story = story
            chapter.save()
            return redirect("chapter_list", story_id=story.id)
    else:
        form = ChapterForm()

    return render(
        request,
        "dash/chapter_form.html",
        {
            "form": form,
            "story": story,
            "mode": "create",
        },
    )


@admin_required
def chapter_edit(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)

    if request.method == "POST":
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            return redirect("chapter_list", story_id=chapter.story.id)
    else:
        form = ChapterForm(instance=chapter)

    return render(
        request,
        "dash/chapter_form.html",
        {
            "form": form,
            "story": chapter.story,
            "mode": "edit",
            "chapter": chapter,
        },
    )





def is_admin(user):
    return user.is_staff


@admin_required
def unlock_chapter(request):
    story_id = request.GET.get("story")
    selected_story = Story.objects.filter(id=story_id).first() if story_id else None

    users = User.objects.all().order_by("name", "phone")
    story_access_map = set()

    if selected_story:
        story_access_map = set(
            StoryAccess.objects.filter(story=selected_story).values_list("user_id", flat=True)
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
def toggle_story_access(request, story_id, user_id):
    if request.method != "POST":
        return redirect("unlock_chapter")

    story = get_object_or_404(Story, id=story_id)
    user = get_object_or_404(User, id=user_id)

    access, created = StoryAccess.objects.get_or_create(user=user, story=story)
    if created:
        messages.success(request, f"Activated {user.phone} for {story.title}.")
    else:
        access.delete()
        messages.info(request, f"Deactivated {user.phone} for {story.title}.")

    return redirect(f"/dashboard/unlock/?story={story.id}")
