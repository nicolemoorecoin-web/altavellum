from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/user/", views.user_home, name="user-home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("overview/", views.OverviewView.as_view(), name="trading"),
    path("plans/", views.PlansView.as_view(), name="plans"),  # <-- now valid
    path("contact/", views.contact, name="contact"),
    path("invest/start/", views.invest_start, name="invest-start"),
     path("dashboard/withdraw/", views.withdraw, name="withdraw"),
]
