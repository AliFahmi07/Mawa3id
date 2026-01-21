from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import date

# Create your models here.


class Profile(models.Model):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        BUSINESS = "business", "Business"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    image = models.ImageField(upload_to="profiles/", null=True, blank=True)

    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Business(models.Model):
    class Category(models.TextChoices):
        PERSONAL_CARE_MALE = "personal_care_male", "Personal Care (Male)"
        PERSONAL_CARE_FEMALE = "personal_care_female", "Personal Care (Female)"
        MEDICAL = "medical", "Medical Health"
        EDUCATION = "education", "Educational & Coaching"
        HOME_SERVICES = "home_services", "Home Services"
        BUSINESS_SERVICES = "business_services", "Business Services"
        PETS = "pets", "Pets"

    owner = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="business"
    )

    name = models.CharField(max_length=255)

    description = models.TextField()

    category = models.CharField(max_length=50, choices=Category.choices)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.owner.role != "business":
            raise ValueError("Only business profiles can create a business.")
        super().save(*args, **kwargs)


class Service(models.Model):
    class Duration(models.TextChoices):
        MIN_15 = "15_min", "15 Minutes"
        MIN_30 = "30_min", "30 Minutes"
        MIN_45 = "45_min", "45 Minutes"
        HOUR_1 = "1_hour", "1 Hour"
        HOUR_1_30 = "1_5_hour", "1 Hour 30 Minutes"
        HOUR_2 = "2_hour", "2 Hours"

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="services"
    )

    description = models.TextField()

    price = models.DecimalField(max_digits=8, decimal_places=2)

    time = models.CharField(max_length=20, choices=Duration.choices)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business.name} - {self.description[:30]}"


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="appointments"
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="appointments"
    )

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="appointments"
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    scheduled_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} → {self.business.name} ({self.status})"

    # Prevent Double Booking (Basic)
    def save(self, *args, **kwargs):
        overlapping = Appointment.objects.filter(
            business=self.business,
            scheduled_at=self.scheduled_at,
            status__in=["pending", "confirmed"],
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValueError("This time slot is already booked.")

    super().save(*args, **kwargs)
