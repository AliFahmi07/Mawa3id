from django.contrib import admin
from .models import Profile, Business, Messages

# Register your models here.

admin.site.register(Profile)
admin.site.register(Business)
admin.site.register(Messages)