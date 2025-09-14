# dashboard/home/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# ✅ if your Investment model lives somewhere else, adjust this import
# e.g. from dashboard.app.models import Investment
try:
    from dashboard.app.models import Investment
except Exception:
    Investment = None  # fail-safe if model path differs

@login_required
def index(request):
    return render(request, 'home/dashboard2.html', {})

@login_required
def investments(request):
    qs = []
    if Investment:
        qs = Investment.objects.select_related('investor').order_by('-date')
    return render(request, 'home/investments.html', {'object_list': qs})

# (optional alias) keep your old route working too
@login_required
def invest(request):
    return investments(request)

@login_required
def plans(request):
  return render(request, "home/plans.html", {})

@login_required
def deposit(request):
    return render(request, 'home/deposit.html', {})

@login_required
def withdraw(request):
    return render(request, 'home/withdraw.html', {})

@login_required
def edit_profile(request):
    return render(request, 'home/profile.html', {})


@login_required
def chart(request):
    return render(request, 'home/charts.html', {})

