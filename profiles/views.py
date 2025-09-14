# profiles/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect

from .models import Profile


@login_required
def edit_profile(request):
    """
    Simple profile editor for the logged-in user.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Update built-in User fields
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name  = request.POST.get("last_name", "").strip()
        request.user.email      = request.POST.get("email", "").strip()
        request.user.save()

        # Update Profile fields
        profile.phone   = request.POST.get("phone", "").strip()
        profile.country = request.POST.get("country", "").strip()
        profile.save()

        messages.success(request, "Profile updated.")
        return redirect("user-home")  # adjust if your dashboard url-name differs

    return render(request, "profiles/edit_profile.html", {"profile": profile})


def register(request):
    """
    Creates a new user with a *hashed* password, ensures Profile exists,
    authenticates and logs the user in, then redirects to the dashboard.
    """
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name", "").strip()
        username   = request.POST.get("username", "").strip()
        email      = request.POST.get("email", "").strip()
        pw1        = request.POST.get("password1", "")
        pw2        = request.POST.get("password2", "")

        if not all([first_name, last_name, username, email, pw1, pw2]):
            messages.error(request, "Please fill out all fields.")
            return render(request, "profiles/register.html")

        if pw1 != pw2:
            messages.error(request, "Passwords do not match.")
            return render(request, "profiles/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, "profiles/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return render(request, "profiles/register.html")

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=pw1,   # hashed automatically
                first_name=first_name,
                last_name=last_name,
            )
            Profile.objects.get_or_create(user=user)

        user = authenticate(request, username=username, password=pw1)
        if user is None:
            messages.error(request, "Could not authenticate the new account.")
            return render(request, "profiles/register.html")

        login(request, user)
        return redirect("user-home")

    return render(request, "profiles/register.html")
