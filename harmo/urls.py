# harmo/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from dashboard.home import views as home_views

# ADD THESE:
from django.conf import settings
from django.conf.urls.static import static

def healthz(request):
    return HttpResponse("OK")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz),
    path("", include("major.urls")),
    path("dashboard/", include("dashboard.home.urls")),
    path("accounts/logout/", home_views.logout_and_home, name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profiles/", include("profiles.urls")),
]

# **Fallback**: if WhiteNoise can’t find a file, Django will serve it from STATIC_ROOT
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
