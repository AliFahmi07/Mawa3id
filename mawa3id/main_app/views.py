from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Business, Profile, Service, Review
from django.urls import reverse

# Create your views here.

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
        business_id = self.kwargs.get('user_id')
        return Business.objects.get(id=business_id)


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
