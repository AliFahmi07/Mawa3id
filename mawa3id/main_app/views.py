from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView,ListView
from .models import Business, Profile, Posts, Service
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Business, Profile, Service, Review
from django.urls import reverse
from django.views import View
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


def home(request):
    return render(request, "home.html")


def signup(request):
    error_message = ""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/profile/create")
        else:
            error_message = "Invalid signup - try again"
    form = UserCreationForm
    context = {"form": form, "error_message": error_message}
    return render(
        request,
        "registration/signup.html",
    )

def posts_index(request):
    posts = Posts.objects.filter(user=request.user)
    return render(request, 'posts/index.html')

def posts_detail(request, posts_id):
    posts = Posts.objects.get(posts=posts_id)
    return render(request, 'posts/detail.html', {'posts': posts})


# ===========================================================================================================
# Profile
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


# ===========================================================================================================
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
        return Business.objects.get(owner = self.request.user)

#===========================================================================================================
#Posts
class PostCreate(CreateView):
    model = Posts
    fields = ['description']

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
