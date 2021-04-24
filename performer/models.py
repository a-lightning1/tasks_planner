from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from authentication.models import User



class Performer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sum_rating = models.FloatField(blank=True,default=0)
    num_responses = models.IntegerField(default=0,blank=True)
    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse("performer_app:performer_page", kwargs={"id": self.id})
    @property
    def rating(self):
        if self.num_responses == 0:
            return 0
        return self.sum_rating / self.num_responses



