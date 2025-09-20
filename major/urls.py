from django.urls import path
from django.views.generic import TemplateView
from .views import OverviewView, HomeView, AboutView, contact, FaqView # ServiceView # PlanView, ServicesView, RoleView, ContactView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('', HomeView.as_view(), name='home'),
  #  path('<str:ref_code>/', Home_View, name='home'),
    #path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('faq/', FaqView.as_view(), name='faq'),
    path('overview/', OverviewView.as_view(), name='trading'),
    path('contact/', contact, name='contact'),
]
