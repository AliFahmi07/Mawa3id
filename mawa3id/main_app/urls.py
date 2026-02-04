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

    # POSTS
    path('posts/', views.posts_index, name='posts_index'),
    path('posts/<int:posts_id>/', views.posts_detail, name='posts_detail'),
    path('posts/create/', views.PostCreate.as_view(), name='posts_create'),
    path('posts/<int:pk>/update/', views.PostUpdate.as_view(), name='posts_update'),
    path('posts/<int:pk>/delete/', views.PostDelete.as_view(), name='posts_delete'),


    path('service/<int:service_id>/review/add/', views.add_review, name='add_review'),
    path('review/<int:pk>/update/', views.ReviewUpdate.as_view(), name='review_update'),
    path('review/<int:pk>/delete/', views.ReviewDelete.as_view(), name='review_delete'),
]
