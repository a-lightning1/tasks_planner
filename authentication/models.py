from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    isCustomer = models.BooleanField(default=False)
    isPerformer = models.BooleanField(default=False)
    @property

        
    def __str__(self):
        if self.is_superuser:
            return "Admin"
        return self.get_name

