from django import forms
from django.core.exceptions import ValidationError
from authentication.models import User
from location.models import City, Location
from location.services import get_cities
GENDER_CHOICES = [
    ('m', 'Male'),
    ('f', 'Female'),
]
class BasicSettingsFormBase(forms.Form):
    about = forms.CharField(max_length=500,label="About me",
                                required=False,widget=forms.Textarea(attrs={"rows":5, "cols":20}))
    location = forms.CharField(
        label="Address",
        widget=forms.TextInput(attrs={"class": "location"}),required=False)
    city = forms.ChoiceField(
        label="City",
        widget=forms.Select(attrs={"class": "selectpicker with-border city","data-live-search":"true"}),required=False)
    birth_date = forms.DateField(label="Date of birth",required=False)
    gender = forms.ChoiceField(
                               choices= GENDER_CHOICES,
                            label="Gender",required=False)
    profile_picture = forms.ImageField(required=False)
    lat = forms.FloatField(required=False, widget=forms.HiddenInput())
    lon = forms.FloatField(required=False, widget=forms.HiddenInput())
    about.widget.attrs.update({"class": "with-border"})
    birth_date.widget.attrs.update({"class": "with-border","id":"datepicker",'autocomplete': 'off',"readonly":"readonly"})
    gender.widget.attrs.update({"class": "selectpicker"})
    profile_picture.widget.attrs.update({"class":"file-upload"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cities = get_cities()
        self.fields['city'].choices = list(
            cities.values_list('value', 'name'))
        self.fields['city'].choices.insert(0,('','Select city'))
    def save(self,user):
        user.profile.about = self.cleaned_data['about']
        user.profile.gender = self.cleaned_data['gender']
        user.profile.birth_date = self.cleaned_data['birth_date']
        city_value = self.cleaned_data['city']
        location_value = self.cleaned_data['location']
        if self.cleaned_data['lat'] and self.cleaned_data['lon'] and city_value:
            lat_value = float(self.cleaned_data['lat'])
            lon_value = float(self.cleaned_data['lon'])
            hh = City.objects.get(value=city_value)
            if user.profile.location:
                if lat_value!=user.profile.location.lat or lon_value != user.profile.location.lon:
                    user.profile.location.lon = lon_value
                    user.profile.location.lat = lat_value
                    user.profile.location.city = hh
                    user.profile.location.address = location_value
                    user.profile.location.save()
            else:
                l = Location(city=hh, lon=lon_value,
                        lat=lat_value, address=location_value)
                l.save()
                user.profile.location = l
        elif not city_value:
            user.profile.location = None
        return user


class BasicSettingsFormPrivatePerson(BasicSettingsFormBase):
    first_name = forms.CharField(max_length=128,label="First name",
                                required=True)
    last_name = forms.CharField(max_length=128, label="Last name",
                                 required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self,user):
        user = BasicSettingsFormBase.save(self,user)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        return user



class BasicSettingsPerformerForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def clean(self):
        super(BasicSettingsPerformerForm, self).clean()





class ChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(max_length=128,widget=forms.PasswordInput(attrs={"class":"with-border"}),label="Current password")
    repeat_password = forms.CharField(max_length=128,widget=forms.PasswordInput(attrs={"class":"with-border"}),label="Repeat password")

    def __init__(self,user,*args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password', None)
        if not self.user.check_password(old_password):
            raise ValidationError('Wrong password!')
        return old_password
    def clean_repeat_password(self):
        password = self.cleaned_data.get('password', None)
        repeat_password = self.cleaned_data.get('repeat_password', None)
        if password != repeat_password:
            raise ValidationError('Passwords should match!')
        return repeat_password

    class Meta:
        model = User
        fields = ("password",)
        labels={"password":"New password"}
        widgets = {
            "password":forms.PasswordInput(attrs={"class":"with-border"})
        }

    def save(self, commit=True):
        m = super(ChangePasswordForm, self).save(commit=False)
        m.set_password(self.cleaned_data["password"])
        if commit:
            m.save()
        return m


class ChangeEmailAndPhoneForm(forms.Form):
    email = forms.EmailField(max_length=128,required=False,label="Email")
    phone_number = forms.CharField(max_length=13,required=False,label="Phone number")

    #TODO clean email and phone

    def save(self,user):
        user.email = self.cleaned_data["email"]
        user.profile.phone_number = self.cleaned_data["phone_number"]
        user.save()
        return user