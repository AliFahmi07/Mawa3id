from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),

    path('profile/create/', views.ProfileCreate.as_view(), name= 'create_profile'),
    path('profile/', views.ProfileDetail.as_view(), name= 'profile_detail'),
    path("profile/update/", views.ProfileUpdateView.as_view(), name="profile_update"),

    path('business/create/', views.BusinessCreate.as_view(), name= 'business_create'),
    path('business/<int:business_id>', views.BusinessDetail.as_view(), name= 'business_detail'),
    path('business/<int:business_id>/update', views.BusinessUpdate.as_view(), name= 'business_update'),

    path('business/<int:business_id>/slot/create', views.TimeSlotCreate.as_view(), name= 'timeslot_create'),
    path('business/<int:business_id>/slot', views.TimeSlotList.as_view(), name= 'timeslot_list'),
    path('slot/<int:pk>/update', views.TimeSlotUpdate.as_view(), name='timeslot_update'),
    path('slot/<int:pk>/delete', views.TimeSlotDelete.as_view(), name='timeslot_delete'),
]
