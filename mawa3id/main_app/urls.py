from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('accounts/signup/', views.signup, name='signup'),
    path('business/create/', views.BusinessCreate.as_view(), name= 'create_business')
]
