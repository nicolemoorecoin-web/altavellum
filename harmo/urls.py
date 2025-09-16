# harmo/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse  # add this
from dashboard.home import views as home_views

def healthz(request):                 # add this
    return HttpResponse("OK")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz),        # add this line
    path("", include("major.urls")),
    path("dashboard/", include("dashboard.home.urls")),
    path("accounts/logout/", home_views.logout_and_home, name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profiles/", include("profiles.urls")),
]
