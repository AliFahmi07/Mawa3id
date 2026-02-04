from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),

    # PROFILE
    path('profile/create/', views.ProfileCreate.as_view(), name= 'create_profile'),
    path('profile/', views.ProfileDetail.as_view(), name= 'profile_detail'),
    path("profile/update/", views.ProfileUpdateView.as_view(), name="profile_update"),

    # BUISENESS
    path('business/create/', views.BusinessCreate.as_view(), name= 'business_create'),
    path('business/show', views.BusinessDetail.as_view(), name= 'business_detail'),
    path('business/<int:pk>/update', views.BusinessUpdate.as_view(), name= 'business_update'),

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
