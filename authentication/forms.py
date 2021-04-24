from django import forms
from django.core.exceptions import ValidationError

from authentication.models import User
from customer.models import Customer
from performer.models import Performer

TYPE_CHOICES = [('c', 'Customer'),
                ('p', 'Employee'), ]

class RegistrationForm(forms.Form):
    username = forms.EmailField(max_length=128)
    first_name = forms.CharField(max_length=128)
    last_name = forms.CharField(max_length=128)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    type = forms.ChoiceField(required=True,
                               choices=TYPE_CHOICES,
                                widget=forms.RadioSelect)
    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1!=password2:
            raise ValidationError("Passwords should match!")
        return password2

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).count():
            raise ValidationError("User with such email already exists!")
        return username

    def save(self):
        new_user = User.objects.create_user(self.cleaned_data["username"],self.cleaned_data["username"],self.cleaned_data["password1"],last_name = self.cleaned_data["last_name"],first_name = self.cleaned_data["first_name"])
        if self.cleaned_data["type"] == 'c':
            new_user.isCustomer = True
            customer = Customer.objects.create(user=new_user)
            customer.save()
        else:
            new_user.isPerformer = True
            performer = Performer.objects.create(user=new_user)
            performer.save()
        new_user.save()
        return new_user
