from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),

    path('profile/create/', views.ProfileCreate.as_view(), name= 'create_profile'),
    path('profile/<int:user_id>', views.ProfileDetail.as_view(), name= 'profile_detail'),

    path('business/create/', views.BusinessCreate.as_view(), name= 'create_business'),
    path('business/<int:user_id>', views.BusinessDetail.as_view(), name= 'business_detail'),


]
