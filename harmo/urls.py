from django.contrib import admin
from django.urls import path, include
from dashboard.home import views as home_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("major.urls")),                 # homepage, about, faq, etc.
    path("dashboard/", include("dashboard.home.urls")),
    path("accounts/logout/", home_views.logout_and_home, name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profiles/", include("profiles.urls")),     # ← fixed path prefix!
]
