from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import User
from accounts.phone import PhoneValidationError, phone_lookup_variants, validate_phone


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
