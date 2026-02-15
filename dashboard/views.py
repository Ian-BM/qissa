from django.shortcuts import render, redirect, get_object_or_404
from stories.models import Story
from stories.forms import StoryForm
from core.utils import admin_required


@admin_required
def dashboard_home(request):
    if not request.user.is_staff:
        return redirect('/')
    
    stories = Story.objects.all()
    return render(request, "dash/home.html", {
        "stories": stories
    })


@admin_required
def story_create(request):
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("dashboard_home")
    else:
        form = StoryForm()

    return render(request, "dash/story_form.html", {
        "form": form,
        "mode": "create"
    })


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

    return render(request, "dash/story_form.html", {
        "form": form,
        "mode": "edit",
        "story": story
    })


@admin_required
def story_toggle_publish(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    story.is_published = not story.is_published
    story.save(update_fields=["is_published"])
    return redirect("dashboard_home")


from stories.models import Story, Chapter
from stories.forms import ChapterForm
from core.utils import admin_required
from django.shortcuts import render, redirect, get_object_or_404


@admin_required
def chapter_list(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    chapters = story.chapters.all()

    return render(request, "dash/chapter_list.html", {
        "story": story,
        "chapters": chapters
    })


@admin_required
def chapter_create(request, story_id):

    if not request.user.staff:
        return redirect('/')

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

    return render(request, "dash/chapter_form.html", {
        "form": form,
        "story": story,
        "mode": "create"
    })


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

    return render(request, "dash/chapter_form.html", {
        "form": form,
        "story": chapter.story,
        "mode": "edit",
        "chapter": chapter
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from accounts.models import User
from stories.models import Chapter
from stories.models import ChapterAccess


def is_admin(user):
    return user.is_staff


@admin_required
def unlock_chapter(request):
    chapters = Chapter.objects.filter(is_locked=True)

    if request.method == "POST":
        phone = request.POST.get("phone")
        chapter_id = request.POST.get("chapter")

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("unlock_chapter")

        chapter = Chapter.objects.get(id=chapter_id)

        ChapterAccess.objects.get_or_create(
            user=user,
            chapter=chapter
        )

        messages.success(request, "Access granted successfully.")
        return redirect("unlock_chapter")

    return render(request, "dash/unlock.html", {
        "chapters": chapters
    })
