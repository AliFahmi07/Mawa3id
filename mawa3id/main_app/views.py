from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from .models import Business, Profile, TimeSlot, Booking
from django.urls import reverse
from django.views import View
from .forms import UserUpdateForm, ProfileUpdateForm, TimeSlotForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .google_calendar import create_event_for_booking, update_event_for_booking, delete_event_for_booking

# Create your views here.

#===========================================================================================================
#Registration

def home(request):
    return render(request, "home.html")


def signup(request):
    error_message = ""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend"
                )
            return redirect("/profile/create/")
        else:
            error_message = "Invalid signup - try again"
    form = UserCreationForm
    context = {"form": form, "error_message": error_message}
    return render(
        request,
        "registration/signup.html",
        context,
    )

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
            return reverse("business_create")
        return reverse("home")


class ProfileDetail(DetailView):
    model = Profile

    def get_object(self):
        return Profile.objects.get(user=self.request.user)


class ProfileUpdateView(View):
    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

        return render(
            request,
            "main_app/profile_update.html",
            {"user_form": user_form, "profile_form": profile_form},
        )

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("/profile")  # change to your profile page

        return render(
            request,
            "profile_update.html",
            {"user_form": user_form, "profile_form": profile_form},
        )


#===========================================================================================================
# Business

class BusinessCreate(CreateView):
    model = Business
    fields = ["name", "description", "category"]
    success_url = "/"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class BusinessDetail(DetailView):
    model = Business
    template_name = "main_app/business_detail.html"

    def get_object(self):
        return Business.objects.filter(owner=self.request.user).first()


class BusinessUpdate(UpdateView):
    model = Business
    fields = ["name", "description", "category"]

    def get_success_url(self):
        return reverse("business_detail", kwargs={"pk": self.object.pk})

#===========================================================================================================
#Appointments

class TimeSlotCreate(CreateView):
    model = TimeSlot
    form_class = TimeSlotForm

    def form_valid(self, form):
        business = get_object_or_404(Business, pk=self.kwargs['business_id'])
        form.instance.business = business

        if business.owner != self.request.user:
            form.add_error(None, "Only the business owner can create time slots.")
            return self.form_invalid(form)

        return super().form_valid(form)


    def get_success_url(self):
        return reverse('business_detail', kwargs={'business_id': self.object.business_id})


class TimeSlotList(ListView):
    model = TimeSlot
    template_name = 'main_app/timeslot_list.html'
    context_object_name = 'slots'

    def get_queryset(self):
        self.business = get_object_or_404(Business, pk=self.kwargs["business_id"])
        return TimeSlot.objects.filter(business=self.business).select_related('service').order_by('start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["business"] = self.business
        return context
