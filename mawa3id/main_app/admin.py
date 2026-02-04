from django.contrib import admin
from .models import Profile, Business, Review, Service

# Register your models here.

admin.site.register(Profile)
admin.site.register(Business)
admin.site.register(Review)
admin.site.register(Service)