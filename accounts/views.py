from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import User


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number input for consistency.
    """
    return phone.replace(" ", "").replace("-", "").strip()


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        phone = normalize_phone(request.POST.get("phone", ""))
        name = request.POST.get("name", "").strip()

        if not phone or not name:
            return render(request, "accounts/register.html", {
                "error": "All fields are required"
            })

        if User.objects.filter(phone=phone).exists():
            return render(request, "accounts/register.html", {
                "error": "Phone number already registered"
            })

        user = User.objects.create_user(
            phone=phone,
            name=name
        )

        login(request, user)
        return redirect("/")

    return render(request, "accounts/register.html")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        phone = normalize_phone(request.POST.get("phone", ""))

        if not phone:
            return render(request, "accounts/login.html", {
                "error": "Phone number is required"
            })

        user = User.objects.filter(phone=phone).first()

        if not user:
            return render(request, "accounts/login.html", {
                "error": "Phone number not registered"
            })

        login(request, user)
        return redirect("/")

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("/login/")
