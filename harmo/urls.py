# harmo/urls.py
from django.contrib import admin
from django.urls import path, include
from dashboard.home import views as home_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("major.urls")),
    path("dashboard/", include("dashboard.home.urls")),
    path("accounts/logout/", home_views.logout_and_home, name="logout"), 
    path("accounts/", include("django.contrib.auth.urls")),   # login/logout/password reset
    path("", include("profiles.urls")),                       # <-- ensures /register works
]
