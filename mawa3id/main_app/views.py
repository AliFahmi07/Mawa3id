from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.utils import timezone
from datetime import datetime
from django.conf import settings
# from allauth.socialaccount.models import SocialAccount
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
from .forms import UserUpdateForm, ProfileUpdateForm, ProfileCreateForm, TimeSlotForm, BusinessEditForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .google_calendar import create_event_for_booking, update_event_for_booking, delete_event_for_booking
import calendar

# Create your views here.

#===========================================================================================================
#Registration

# views.py

from .models import Business, Profile

def home(request):
    businesses = Business.objects.all().order_by("category", "name")

    if request.user.is_authenticated and request.user.profile.role == Profile.Role.BUSINESS_OWNER:
        businesses = Business.objects.none()

    selected_category = request.GET.get("category")

    if selected_category:
        businesses = businesses.filter(category=selected_category)

    context = {
        "businesses": businesses,
        "categories": Business.Category.choices,
        "selected_category": selected_category,
    }

    return render(request, "home.html", context)



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

            # Redirect based on role
            if profile.role == "business_owner":
                return redirect("business_create")
            else:
                return redirect("home")  # default fallback



        else:
            error_message = "Invalid signup - try again"

    user_form = UserCreationForm()
    profile_form = ProfileCreateForm()

    context = {"user_form": user_form, "profile_form": profile_form, "error_message": error_message}
    return render(
        request,
        "registration/signup.html", context
    )

def posts_index(request):
    user_profile = request.user.profile

    if user_profile.role == Profile.Role.CLIENT:
        posts = Posts.objects.filter(user=request.user)
    else:
        posts = Posts.objects.exclude(user=request.user)

    return render(request, 'posts/index.html', {'posts': posts})

def posts_detail(request, posts_id):
    posts = Posts.objects.get(id=posts_id)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        if profile.role == Profile.Role.BUSINESS_OWNER:
            business = Business.objects.filter(owner=self.request.user).first()
            if business:
                all_reviews = Review.objects.filter(service__business=business)
                context['all_reviews'] = all_reviews

                if all_reviews.exists():
                    total_rating = 0
                    for review in all_reviews:
                        total_rating += review.rating
                    avg_rating = total_rating / all_reviews.count()
                    context['average_rating']= round(avg_rating, 1)
                else:
                    context['average_rating']=  0

        return context



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
            return redirect("/profile")

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

        if Business.objects.filter(owner=user).exists():
            form.add_error(None, "you already have a business")
            return self.form_invalid(form)

        form.instance.owner = self.request.user
        return super().form_valid(form)


# AI >>>>>>>>>>>>>>>>>>>>>>>>>
class BusinessDashboard(LoginRequiredMixin, View):
    template_name = "main_app/business_dashboard.html"

    class BusinessEditForm(forms.ModelForm):
        class Meta:
            model = Business
            fields = ["name", "description", "category"]

    def _get_business(self, request):
        return get_object_or_404(Business, owner=request.user)

    def _get_year_month(self, request):
        today = timezone.localdate()
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        month = max(1, min(12, month))
        return year, month

    def _month_grid_with_bookings(self, business, year, month):
        first_day = timezone.datetime(year, month, 1).date()
        weeks = calendar.monthcalendar(year, month)

        month_start = timezone.make_aware(
            timezone.datetime(year, month, 1, 0, 0, 0)
        )
        if month == 12:
            next_month_start = timezone.make_aware(timezone.datetime(year + 1, 1, 1, 0, 0, 0))
        else:
            next_month_start = timezone.make_aware(timezone.datetime(year, month + 1, 1, 0, 0, 0))

        bookings = (
            Booking.objects
            .filter(slot__business=business, slot__start__gte=month_start, slot__start__lt=next_month_start)
            .select_related("slot", "client", "slot__service")
            .order_by("slot__start")
        )

        by_day = {}
        for b in bookings:
            d = timezone.localtime(b.slot.start).date().day
            by_day.setdefault(d, []).append(b)

        grid = []
        for week in weeks:
            row = []
            for day_num in week:
                row.append({
                    "day": day_num,
                    "bookings": by_day.get(day_num, []) if day_num != 0 else [],
                })
            grid.append(row)

        return grid

    def get(self, request):
        business = self._get_business(request)
        year, month = self._get_year_month(request)

        business_form = self.BusinessEditForm(instance=business)
        weeks = self._month_grid_with_bookings(business, year, month)

        bookings = (
            Booking.objects
            .filter(slot__business=business)
            .select_related("slot", "client", "slot__service", "slot__business")
            .order_by("-slot__start")
        )

        calendar_src = None

        has_google = SocialAccount.objects.filter(
            user=business.owner,
            provider="google"
        ).exists()

        owner = business.owner
        google_account = SocialAccount.objects.filter(user=owner, provider="google").first()

        if google_account:
            calendar_src = google_account.extra_data.get("email") or owner.email

        context = {
            "business": business,
            "business_form": business_form,
            "bookings": bookings,
            "bookings_count": bookings.count(),
            "year": year,
            "month": month,
            "weeks": weeks,
            "calendar_src": calendar_src,
            "calendar_tz": getattr(settings, "TIME_ZONE", "UTC"),
            "has_google": has_google,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        business = self._get_business(request)
        year, month = self._get_year_month(request)

        business_form = self.BusinessEditForm(request.POST, instance=business)
        if business_form.is_valid():
            business_form.save()
            return redirect("business_dashboard")

        weeks = self._month_grid_with_bookings(business, year, month)

        context = {
            "business": business,
            "business_form": business_form,
            "year": year,
            "month": month,
            "weeks": weeks,
        }
        return render(request, self.template_name, context)

    #AI <<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class BusinessDetail(DetailView):
    model = Business
    template_name = "main_app/business_detail.html"

    def get_object(self):
        return get_object_or_404(Business, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = list(self.object.services.all())

        if self.request.user.is_authenticated:
            for service in services:
                service.user_review = service.reviews.filter(user=self.request.user).first()
        context['services'] = services
        return context

# AI >>>>>>>>>>>>>>>>>>>>>>>>>
class BusinessDashboard(LoginRequiredMixin, View):
    template_name = "main_app/business_dashboard.html"

    class BusinessEditForm(forms.ModelForm):
        class Meta:
            model = Business
            fields = ["name", "description", "category"]

    def _get_business(self, request):
        return get_object_or_404(Business, owner=request.user)

    def _get_year_month(self, request):
        today = timezone.localdate()
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        month = max(1, min(12, month))
        return year, month

    def _month_grid_with_bookings(self, business, year, month):
        first_day = timezone.datetime(year, month, 1).date()
        weeks = calendar.monthcalendar(year, month)

        month_start = timezone.make_aware(
            timezone.datetime(year, month, 1, 0, 0, 0)
        )
        if month == 12:
            next_month_start = timezone.make_aware(timezone.datetime(year + 1, 1, 1, 0, 0, 0))
        else:
            next_month_start = timezone.make_aware(timezone.datetime(year, month + 1, 1, 0, 0, 0))

        bookings = (
            Booking.objects
            .filter(slot__business=business, slot__start__gte=month_start, slot__start__lt=next_month_start)
            .select_related("slot", "client", "slot__service")
            .order_by("slot__start")
        )

        by_day = {}
        for b in bookings:
            d = timezone.localtime(b.slot.start).date().day
            by_day.setdefault(d, []).append(b)

        grid = []
        for week in weeks:
            row = []
            for day_num in week:
                row.append({
                    "day": day_num,
                    "bookings": by_day.get(day_num, []) if day_num != 0 else [],
                })
            grid.append(row)

        return grid

    def get(self, request):
        business = self._get_business(request)
        year, month = self._get_year_month(request)

        business_form = self.BusinessEditForm(instance=business)
        weeks = self._month_grid_with_bookings(business, year, month)

        bookings = (
            Booking.objects
            .filter(slot__business=business)
            .select_related("slot", "client", "slot__service", "slot__business")
            .order_by("-slot__start")
        )

        calendar_src = None

        has_google = SocialAccount.objects.filter(
            user=business.owner,
            provider="google"
        ).exists()

        owner = business.owner
        google_account = SocialAccount.objects.filter(user=owner, provider="google").first()

        if google_account:
            calendar_src = google_account.extra_data.get("email") or owner.email

        context = {
            "business": business,
            "business_form": business_form,
            "bookings": bookings,
            "bookings_count": bookings.count(),
            "year": year,
            "month": month,
            "weeks": weeks,
            "calendar_src": calendar_src,
            "calendar_tz": getattr(settings, "TIME_ZONE", "UTC"),
            "has_google": has_google,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        business = self._get_business(request)
        year, month = self._get_year_month(request)

        business_form = self.BusinessEditForm(request.POST, instance=business)
        if business_form.is_valid():
            business_form.save()
            return redirect("business_dashboard")

        weeks = self._month_grid_with_bookings(business, year, month)

        context = {
            "business": business,
            "business_form": business_form,
            "year": year,
            "month": month,
            "weeks": weeks,
        }
        return render(request, self.template_name, context)

    #AI <<<<<<<<<<<<<<<<<<<<<<<<<<<<<


#===========================================================================================================
#POSTS

class PostCreate(CreateView):
    model = Posts
    fields = ['description', 'price']
    template_name = 'posts/posts_form.html'
    success_url = '/posts/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdate(UpdateView):
    model = Posts
    fields = ['description', 'price']
    template_name = 'posts/posts_form.html'
    success_url = '/posts/'

    def get_queryset(self):
        return Posts.objects.filter(user=self.request.user)

class PostDelete(DeleteView):
    model = Posts
    template_name = 'posts/posts_confirm_delete.html'
    success_url = '/posts/'

    def get_queryset(self):
        return Posts.objects.filter(user=self.request.user)

def post_accept(request, posts_id):
    post = Posts.objects.get(id=posts_id)

    if request.user.profile.role != 'business_owner':
        return redirect('posts_index')

    if post.user == request.user:
        return redirect('posts_index')

    if post.business:
        return redirect('posts_index')

    if not Business.objects.filter(owner=request.user).exists():
        return redirect('business_create')

    business = Business.objects.get(owner=request.user)
    post.business = business
    post.save()

    return render(request, 'posts/post_accepted.html', {'post': post})

class BusinessUpdate(UpdateView):
    model = Business
    fields = ["name", "description", "category"]

    def get_queryset(self): # to update the user's business only
        return Business.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse("business_detail", kwargs={'pk':self.request.user.id})


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

    def get_slot(self):
        return get_object_or_404(TimeSlot, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot = self.get_slot()
        context['slot'] = slot
        context['business'] = slot.business
        context['now'] = timezone.now()
        return context


    def form_valid(self, form):
        slot = self.get_slot()
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
    fields = ["status"]
    template_name="main_app/booking_form.html"

    def get_queryset(self):
        return Booking.objects.filter(client=self.request.user)

    def form_valid(self, form):

        response = super().form_valid(form)

        try:
            update_event_for_booking(self.object)
        except Exception:
            pass

        return response

    def get_success_url(self):
            return reverse("timeslot_list", kwargs={"pk": self.object.slot.business_id})


class BookingStatusUpdate(UpdateView):
        model = Booking
        fields = ['status']

        def get_queryset(self):
            return Booking.objects.filter(slot__business__owner=self.request.user)

        def form_valid(self, form):
            response = super().form_valid(form)

            try:
                update_event_for_booking(self.object)
            except Exception:
                pass

            return response

        def get_success_url(self):
            return reverse("business_dashboard")


class BookingDelete(DeleteView):
    model = Booking

    def get_queryset(self):
        return Booking.objects.filter(client=self.request.user)

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
    fields = ["name", "description", "time", "price"]

    def form_valid(self, form):
        form.instance.business = Business.objects.get(owner = self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('business_detail', kwargs={'pk':self.object.business.id})



class ServiceDetail(DetailView):
    model = Service
    template_name = "main_app/service_detail.html"

    def get_object(self):
        return get_object_or_404(Service, id=self.kwargs["service_id"])

class ServiceUpdate(UpdateView):
    model = Service
    fields = ["name", "description", "time", "price"]
    template_name = 'main_app/service_form.html'

    def get_object(self, queryset=None):
        service_id = self.kwargs.get("service_id")
        # Filter service that belongs to the business
        return get_object_or_404(Service, id=service_id)

    def get_success_url(self):
        return reverse("business_detail", kwargs={"pk": self.kwargs.get("pk")})

class ServiceDelete(DeleteView):
    model = Service
    pk_url_kwarg = "service_id"

    def get_success_url(self):
        return reverse("business_detail", kwargs={"pk": self.kwargs["pk"]})

#===========================================================================================================
#Review

class ReviewCreate(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'text']
    template_name = 'main_app/review_form.html'

    def form_valid(self, form):
        service = get_object_or_404(Service, id=self.kwargs['service_id'])

        if self.request.user.profile.role != Profile.Role.CLIENT:
            return redirect("business_detail", pk=service.business_id)

        if Review.objects.filter(service=service, user=self.request.user).exists():
            return redirect("business_detail", pk=service.business_id)

        form.instance.service = service
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("business_detail", kwargs={"pk": self.object.service.business_id})


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    model = Review
    fields = ['rating', 'text']
    template_name = 'main_app/review_form.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("business_detail", kwargs={"pk": self.object.service.business_id})


class ReviewDelete(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'main_app/review_confirm_delete.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("business_detail", kwargs={"pk": self.object.service.business_id})



#===========================================================================================================
