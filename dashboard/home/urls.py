from django.urls import path
from . import views

urlpatterns = [
    path("user/",        views.index,        name="user-home"),
    path("invest/",      views.invest,       name="invest"),
    path("plans/",       views.plans,        name="plans"),      # <— NEW
    path("deposit/",     views.deposit,      name="deposit"),
    path("withdraw/",    views.withdraw,     name="withdraw"),
    path("investments/", views.investments,  name="investments"),
    path("profile/",     views.edit_profile, name="edit_profile"),
    path("chart/",       views.chart,        name="chart"),
]
