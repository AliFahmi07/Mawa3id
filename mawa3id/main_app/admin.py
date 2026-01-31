from django.contrib import admin
from .models import Profile, Business, TimeSlot, Booking

# Register your models here.

admin.site.register(Profile)
admin.site.register(Business)
admin.site.register(TimeSlot)
admin.site.register(Booking)

