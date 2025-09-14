from django.urls import path
from .views import OverviewView, HomeView, AboutView, contact, FaqView # ServiceView # PlanView, ServicesView, RoleView, ContactView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
  #  path('<str:ref_code>/', Home_View, name='home'),
    #path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('faq/', FaqView.as_view(), name='faq'),
    path('overview/', OverviewView.as_view(), name='trading'),
    path('contact/', contact, name='contact'),
]