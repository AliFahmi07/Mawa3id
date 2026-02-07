from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from .models import Business, Profile, Posts, Service
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Business, Profile, Service, Review, TimeSlot, Booking
from django.urls import reverse
from django.views import View
from .forms import UserUpdateForm, ProfileUpdateForm, ProfileCreateForm, TimeSlotForm
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
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileCreateForm(request.POST, request.FILES)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            profile = profile_form.save(commit=False)
            user.save()
            profile.user = user
            profile.save()
            login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0],)
            return redirect("/profile")
        else:
            error_message = "Invalid signup - try again"

    user_form = UserCreationForm
    profile_form = ProfileCreateForm

    context = {"user_form": user_form, "profile_form": profile_form ,"error_message": error_message}
    return render(
        request,
        "registration/signup.html", context
    )

def posts_index(request):
    posts = Posts.objects.filter(user=request.user)
    return render(request, 'posts/index.html')

def posts_detail(request, posts_id):
    posts = Posts.objects.get(posts=posts_id)
    return render(request, 'posts/detail.html', {'posts': posts})


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
        user = self.request.user

        if Business.objects.get(owner = user) :
            form.add_error(None, "you already have a business")
            return self.form_invalid(form)
        else:
            form.instance.owner = self.request.user
            return super().form_valid(form)


class BusinessDetail(DetailView):
    model = Business
    template_name = "main_app/business_detail.html"

    def get_object(self):
        return Business.objects.get(owner = self.request.user)

#===========================================================================================================
#Posts
class PostCreate(CreateView):
    model = Posts
    fields = ['description']
    template_name = 'posts/posts_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PostUpdate(UpdateView):
    model = Posts
    fields = ['description']

class PostDelete(DeleteView):
    model = Posts
    success_url = '/posts/'


class BusinessUpdate(UpdateView):
    model = Business
    fields = ["name", "description", "category"]

    def get_queryset(self): # to update the user's business only
        return Business.objects.filter(owner=self.request.user)

    def get_success_url(self):

        return reverse("business_detail")


class BusinessList(ListView):
    model = Business
    template_name = "main_app/businesses"

#===========================================================================================================
#Appointments

class TimeSlotCreate(CreateView):
    model = TimeSlot
    form_class = TimeSlotForm

    def form_valid(self, form):
        business = get_object_or_404(Business, pk=self.kwargs['pk'])
        form.instance.business = business

        if business.owner != self.request.user:
            form.add_error(None, "Only the business owner can create time slots.")
            return self.form_invalid(form)

        return super().form_valid(form)


    def get_success_url(self):
        return reverse('timeslot_list', kwargs={'pk': self.object.business_id})


class TimeSlotList(ListView):
    model = TimeSlot
    template_name = 'main_app/timeslot_list.html'
    context_object_name = 'slots'

    def get_queryset(self):
        self.business = get_object_or_404(Business, pk=self.kwargs["pk"])
        return TimeSlot.objects.filter(business=self.business).select_related('service').order_by('start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["business"] = self.business
        return context


class TimeSlotUpdate(UpdateView):
    model = TimeSlot
    form_class = TimeSlotForm

    def get_success_url(self):
        return reverse("timeslot_list", kwargs={"pk": self.object.business_id})


class TimeSlotDelete(DeleteView):
    model = TimeSlot

    def get_success_url(self):
        return reverse("timeslot_list", kwargs={"pk": self.object.business_id})


class BookingCreate(CreateView):
    model = Booking
    fields = ['notes']

    def form_valid(self, form):
        slot = get_object_or_404(TimeSlot, pk=self.kwargs["pk"])


        if not slot.is_active:
            form.add_error(None, "This slot is not available.")
            return self.form_invalid(form)

        if hasattr(slot, "booking"):
            form.add_error(None, "This slot is already booked, please choose another slot.")
            return self.form_invalid(form)

        if slot.start <= timezone.now():
            form.add_error(None, "Please just an appropriate time!")
            return self.form_invalid(form)


        form.instance.slot = slot
        form.instance.client = self.request.user
        form.instance.status = Booking.Status.PENDING

        response = super().form_valid(form)

        try:
            create_event_for_booking(self.object)
        except Exception:
            pass

        return response


    def get_success_url(self):
        return reverse("timeslot_list", kwargs={"pk": self.object.slot.business_id})

class BookingUpdate(UpdateView):
    model = Booking
    fields = [""]
    template_name="main_app/booking_form.html"

    def get_queryset(self):
        return Booking.objects.filter(client=self.request.user)

    def form_valid(self, form):

        response = super().form_valid(form)

        try:
            create_event_for_booking(self.object)
        except Exception:
            pass

        return response

    def get_success_url(self):
        return reverse("timeslot_list", kwargs={"pk": self.object.slot.business_id})


class BookingDelete(DeleteView):
    model = Booking

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            delete_event_for_booking(self.object)
        except Exception:
            pass
        
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("timeslot_list", kwargs={"pk": self.object.business_id})

# ===========================================================================================================
# Service

class ServiceCreate(CreateView):
    model = Service
    success_url = "/business/show"
    fields = ["name", "description", "time", "price"]
    def form_valid(self, form):
        form.instance.business_id = Business.objects.get(owner = self.request.user).id
        return super().form_valid(form)



class ServiceDetail(DetailView):
    model = Service
    template_name = "main_app/service_detail.html"

    def get_object(self):
        return Service.objects.get(id=self.kwargs["service_id"])
class ServiceUpdate(UpdateView):
    model = Service
    fields = ["name", "description", "time", "price"]
    template_name = 'main_app/service_form.html'

    def get_success_url(self):
        return reverse("service_detail", kwargs={'service_id': self.object.id})


class ServiceDelete(DeleteView):
    model = Service
    success_url = "/business/show"

#===========================================================================================================
#Review

@login_required
def add_review(request, service_id):
    """Add a review to a service - prevents duplicates"""
    service = get_object_or_404(Service, id=service_id)

    # Check if user already reviewed this service
    if Review.objects.filter(service=service, user=request.user).exists():
        return redirect('home')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text', '').strip()

        # Validate
        if rating and text and len(text) <= 500:
            Review.objects.create(
                service=service,
                user=request.user,
                rating=int(rating),
                text=text
            )

    return redirect('home')


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    model = Review
    fields = ['rating', 'text']
    template_name = 'main_app/review_form.html'
    success_url = '/'


class ReviewDelete(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'main_app/review_confirm_delete.html'
    success_url = '/'



#===========================================================================================================
