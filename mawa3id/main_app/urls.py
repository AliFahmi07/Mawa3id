from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),

    path('profile/create/', views.ProfileCreate.as_view(), name= 'create_profile'),
    path('profile/', views.ProfileDetail.as_view(), name= 'profile_detail'),
    path("profile/update/", views.ProfileUpdateView.as_view(), name="profile_update"),

    path('business/create/', views.BusinessCreate.as_view(), name= 'business_create'),
    path('business/<int:pk>', views.BusinessDetail.as_view(), name= 'business_detail'),
    path('business/<int:pk>/update', views.BusinessUpdate.as_view(), name= 'business_update'),



]
