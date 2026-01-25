from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        BUSINESS_OWNER = "business_owner", "Business Owner"

    user = models.ForeignKey(User, on_delete=models.CASCADE),
    image = image = models.ImageField(upload_to="main_app/static/uploads", default="")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT,)

    def __str__(self):
        return f"{self.user} ({self.role})"
