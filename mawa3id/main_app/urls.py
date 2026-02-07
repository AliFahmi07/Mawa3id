from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),

    # PROFILE
    path('profile/create/', views.ProfileCreate.as_view(), name= 'create_profile'),
    path('profile/', views.ProfileDetail.as_view(), name= 'profile_detail'),
    path("profile/update/", views.ProfileUpdateView.as_view(), name="profile_update"),

    # BUSINESS
    path('business/create/', views.BusinessCreate.as_view(), name= 'business_create'),
    path('business/<int:pk>/', views.BusinessDetail.as_view(), name= 'business_detail'),
    path('business/<int:pk>/update', views.BusinessUpdate.as_view(), name= 'business_update'),

    # APPOINTMENTS
    path('business/<int:pk>/slot/create', views.TimeSlotCreate.as_view(), name= 'timeslot_create'),
    path('business/<int:pk>/slot', views.TimeSlotList.as_view(), name= 'timeslot_list'),
    path('slot/<int:pk>/update', views.TimeSlotUpdate.as_view(), name='timeslot_update'),
    path('slot/<int:pk>/delete', views.TimeSlotDelete.as_view(), name='timeslot_delete'),

    path('slot/<int:pk>/book', views.BookingCreate.as_view(), name='booking_create'),
    path('booking/<int:pk>/update', views.BookingUpdate.as_view(), name='booking_update'),
    path('booking/<int:pk>/delete', views.BookingDelete.as_view(), name='booking_delete'),


    # SERVICE
    path('business/service/create/', views.ServiceCreate.as_view(), name= 'service_create'),
    path('business/service/<int:service_id>', views.ServiceDetail.as_view(), name= 'service_detail'),
    path('business/service/<int:pk>/update/', views.ServiceUpdate.as_view(), name= 'service_update'),
    path('business/service/<int:pk>/delete', views.ServiceDelete.as_view(), name= 'service_delete'),

    # POSTS
    path('posts/', views.posts_index, name='posts_index'),
    path('posts/<int:posts_id>/', views.posts_detail, name='posts_detail'),
    path('posts/create/', views.PostCreate.as_view(), name='posts_create'),
    path('posts/<int:pk>/update/', views.PostUpdate.as_view(), name='posts_update'),
    path('posts/<int:pk>/delete/', views.PostDelete.as_view(), name='posts_delete'),

    # REVIEW
    path('service/<int:service_id>/review/add/', views.add_review, name='add_review'),
    path('review/<int:pk>/update/', views.ReviewUpdate.as_view(), name='review_update'),
    path('review/<int:pk>/delete/', views.ReviewDelete.as_view(), name='review_delete'),
]
