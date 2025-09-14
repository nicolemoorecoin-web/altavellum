from email import message
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
#from .models import Post
from django.shortcuts import render
from .forms import ContactForm
from .models import Contact
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader


# Create your views here.


class HomeView(TemplateView):
    template_name = 'index.html'
    ordering = ['-post_date']

class OverviewView(TemplateView):
    template_name = 'trading.html'

class AboutView(TemplateView):
    template_name = 'about.html'

class FaqView(TemplateView):
    template_name = 'faq.html'

def contact(request):
    success_message = None

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']

            # Create a new Contact instance and save it
            contact = Contact(message=message, name=name, email=email, subject=subject)
            contact.save()

            # Render the email template as a string
            html_message = loader.render_to_string('contact_email.html', {'name': name, 'email': email, 'subject': subject, 'message': message})

            # Send email
            send_mail(
                f"New Contact: {subject}",
                f"Name: {name}\nEmail: {email}\n\n{message}",
                settings.EMAIL_HOST_USER,  # Send from the user's email address
                ['badguybadguy79@gmail.com'],  # Send to the particular email address
                fail_silently=True,
                html_message=html_message,
            )

            success_message = "Form submitted successfully!"

    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form, 'success_message': success_message})