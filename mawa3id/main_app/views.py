from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from .models import Business, Profile, TimeSlot, Booking
from django.urls import reverse
from .google_calendar import create_event_for_booking, update_event_for_booking, delete_event_for_booking

# Create your views here.

#===========================================================================================================
#Registration

def home(request):
    return render(request, 'home.html')


def signup(request):
    error_message=''
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            return redirect('/profile/create')
        else:
            error_message = 'Invalid signup - try again'
    form = UserCreationForm
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', )

#===========================================================================================================
#Profile

class ProfileCreate(CreateView):
    model = Profile
    fields = ["image", "role"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.role == Profile.Role.BUSINESS_OWNER:
            return reverse("create_business")
        return reverse("home")

class ProfileDetail(DetailView):
    model = Profile
    template_name = 'main_app/profile_detail.html'

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

#===========================================================================================================
#Business

class BusinessCreate(CreateView):
    model = Business
    fields = ['name', 'description', 'category']
    success_url = '/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class BusinessDetail(DetailView):
    model = Business
    template_name = 'main_app/business_detail.html'

    def get_object(self):
        return Business.objects.get(owner = self.request.user)

#===========================================================================================================
#Appointments

class TimeSlotCreate(CreateView):
    model = TimeSlot
    fields = ['start','duration', 'service']

    def form_valid(self, form):


        return super().form_valid(form)

