from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import User


from .phone import (
    EAST_AFRICAN_COUNTRY_CHOICES,
    PhoneValidationError,
    validate_east_african_phone,
)


def _auth_form_context(**extra):
    context = {
        "country_choices": EAST_AFRICAN_COUNTRY_CHOICES,
        "selected_country_code": "+255",
        "phone_number": "",
        "name": "",
    }
    context.update(extra)
    return context


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        selected_country_code = request.POST.get("country_code", "+255")
        phone_number = request.POST.get("phone_number", "")

        try:
            phone = validate_east_african_phone(selected_country_code, phone_number)
        except PhoneValidationError as exc:
            return render(request, "accounts/register.html", _auth_form_context(
                error=str(exc),
                name=name,
                selected_country_code=selected_country_code,
                phone_number=phone_number,
            ))

        if not name:
            return render(request, "accounts/register.html", _auth_form_context(
                error="All fields are required",
                name=name,
                selected_country_code=selected_country_code,
                phone_number=phone_number,
            ))

        if User.objects.filter(phone=phone).exists():
            return render(request, "accounts/register.html", _auth_form_context(
                error="Phone number already registered",
                name=name,
                selected_country_code=selected_country_code,
                phone_number=phone_number,
            ))

        user = User.objects.create_user(
            phone=phone,
            name=name
        )

        login(request, user)
        return redirect("/")

    return render(request, "accounts/register.html", _auth_form_context())


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        selected_country_code = request.POST.get("country_code", "+255")
        phone_number = request.POST.get("phone_number", "")

        try:
            phone = validate_east_african_phone(selected_country_code, phone_number)
        except PhoneValidationError as exc:
            return render(request, "accounts/login.html", _auth_form_context(
                error=str(exc),
                selected_country_code=selected_country_code,
                phone_number=phone_number,
            ))

        user = User.objects.filter(phone=phone).first()

        if not user:
            return render(request, "accounts/login.html", _auth_form_context(
                error="Phone number not registered",
                selected_country_code=selected_country_code,
                phone_number=phone_number,
            ))

        login(request, user)
        return redirect("/")

    return render(request, "accounts/login.html", _auth_form_context())


@login_required
def logout_view(request):
    logout(request)
    return redirect("/login/")
