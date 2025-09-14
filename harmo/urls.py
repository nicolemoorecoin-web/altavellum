# harmo/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("major.urls")),
    path("dashboard/", include("dashboard.home.urls")),
    path("accounts/", include("django.contrib.auth.urls")),   # login/logout/password reset
    path("", include("profiles.urls")),                       # <-- ensures /register works
]
