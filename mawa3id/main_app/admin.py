from django.contrib import admin
from .models import Profile, Business, Review, Service, TimeSlot, Booking, Posts

# Register your models here.

admin.site.register(Profile)
admin.site.register(Business)
admin.site.register(TimeSlot)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Service)
admin.site.register(Posts)
