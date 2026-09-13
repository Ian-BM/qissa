from datetime import timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.models import User
from accounts.phone import PhoneValidationError, phone_lookup_variants, validate_phone
from shorts.models import ShortStory
from stories.models import Story, StoryReaction


def _auth_form_context(**extra):
    context = {
        "phone": "",
        "name": "",
    }
    context.update(extra)
    return context


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone_input = request.POST.get("phone", "")

        try:
            phone = validate_phone(phone_input)
        except PhoneValidationError as exc:
            return render(
                request,
                "accounts/register.html",
                _auth_form_context(
                    error=str(exc),
                    name=name,
                    phone=phone_input,
                ),
            )

        if not name:
            return render(
                request,
                "accounts/register.html",
                _auth_form_context(
                    error="All fields are required",
                    name=name,
                    phone=phone_input,
                ),
            )

        if User.objects.filter(phone__in=phone_lookup_variants(phone)).exists():
            return render(
                request,
                "accounts/register.html",
                _auth_form_context(
                    error="Phone number already registered",
                    name=name,
                    phone=phone_input,
                ),
            )

        user = User.objects.create_user(phone=phone, name=name)
        login(request, user)
        return redirect("/")

    return render(request, "accounts/register.html", _auth_form_context())


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        phone_input = request.POST.get("phone", "")

        try:
            phone_variants = phone_lookup_variants(phone_input)
        except PhoneValidationError as exc:
            return render(
                request,
                "accounts/login.html",
                _auth_form_context(
                    error=str(exc),
                    phone=phone_input,
                ),
            )

        user = User.objects.filter(phone__in=phone_variants).first()

        if not user:
            return render(
                request,
                "accounts/login.html",
                _auth_form_context(
                    error="Phone number not registered",
                    phone=phone_input,
                ),
            )

        login(request, user)
        return redirect("/")

    return render(request, "accounts/login.html", _auth_form_context())


@login_required
def logout_view(request):
    logout(request)
    return redirect("/login/")


@login_required
def dashboard_view(request):
    user = request.user
    recent_cutoff = timezone.now() - timedelta(days=7)

    liked_story_ids = StoryReaction.objects.filter(
        user=user, value=StoryReaction.LIKE
    ).values_list("story_id", flat=True)
    liked_stories = Story.objects.filter(id__in=liked_story_ids, is_published=True)

    liked_shorts = ShortStory.objects.filter(
        story_likes__user=user, published=True
    ).distinct()

    recent_stories = Story.objects.filter(
        is_published=True, created_at__gte=recent_cutoff
    ).order_by("-created_at")[:6]

    renew_soon = bool(
        user.is_subscription_active()
        and user.premium_end
        and user.premium_end - timezone.now().date() <= timedelta(days=7)
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "liked_stories": liked_stories,
            "liked_shorts": liked_shorts,
            "recent_stories": recent_stories,
            "renew_soon": renew_soon,
        },
    )
