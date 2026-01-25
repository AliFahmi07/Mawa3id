from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        BUSINESS_OWNER = "business_owner", "Business Owner"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = image = models.ImageField(upload_to="main_app/static/uploads"
        default=""
        )
    role = models.CharField(
        choices=Role.choices,
        default=Role.CLIENT,
        )

    def __str__(self):
        return f"{self.user} ({self.role})"

class Business(models.Model):
    class Category(models.TextChoices):
        BARBER = "barber", "Barber"
        DENTIST = "dentist", "Dentist"
        GYM = "gym", "Gym"
        SALON = "salon", "Salon"
        CLINIC = "clinic", "Clinic"
        OTHER = "other", "Other"
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business")
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    category = models.CharField(
        choices=Category.choices
        default=Category.OTHER
        )

    def __str__(self):
        return self.name

class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.FloatField()
    def __str__(self):
        return f"Job Post by {self.user.username} - ${self.price}"
        