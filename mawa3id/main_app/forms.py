from django import forms
from django.contrib.auth.models import User
from .models import Profile, TimeSlot

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image"]

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["service", "start", "duration"]
        widgets = {
            "start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class ProfileCreateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image", "role"]
