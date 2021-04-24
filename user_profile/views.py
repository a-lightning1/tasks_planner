from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic.base import View
from location.models import City
from performer.models import Performer
from user_profile.forms import BasicSettingsFormPrivatePerson, ChangePasswordForm, \
    ChangeEmailAndPhoneForm, BasicSettingsPerformerForm
from order.models import SimpleOrder, OrderStatus
from customer.models import Customer
from chat.models import Message
from order.services import get_orders



class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        messages = Message.objects.filter(message_to=request.user,is_read=False)
        if request.user.isCustomer:
            status = request.GET.get('status', None)
            if status:
                status = get_object_or_404(OrderStatus, value=status)
            customer = get_object_or_404(Customer, user=request.user)
            orders = get_orders(status=status, customer=customer, per_page=100) # tmp
            active_tasks = len(SimpleOrder.objects.filter(customer=customer))
        else:
            performer = get_object_or_404(Performer, user=request.user)
            active_tasks = len(SimpleOrder.objects.filter(performer=performer))
            orders = get_orders(performer=request.user.performer)

        return render(request, 'user_profile/profile.html', {
            'orders': orders,
            'messages':messages,
            "active_tasks":active_tasks
        })


class BasicSettingsView(LoginRequiredMixin, View):
    def make_context(self,request):
        user = request.user
        location = user.profile.location
        city = ""
        address = ""
        if location:
            city = location.city.value
            address = location.address
        data = {
            "about": user.profile.about,
            "birth_date": user.profile.birth_date,
            "phone_number": user.profile.phone_number,
            "gender": user.profile.gender,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "city": city,
            "location": address
        }
        if location:
            data['lat'] = location.lat
            data['lon'] = location.lon
        else:
            data["birth_date"] = user.profile.birth_date
            data["gender"] = user.profile.gender
            data["first_name"] = user.first_name
            data["last_name"] = user.last_name
            basic_settings_form = BasicSettingsFormPrivatePerson(data)
        context = {"base_settings_form": basic_settings_form}
        if user.isPerformer:
            data_performer = {}
            basic_settings_performer_form = BasicSettingsPerformerForm(data_performer)
            context["basic_settings_performer_form"] = basic_settings_performer_form
        return context
    def get(self, request):
        context = self.make_context(request)
        return render(request, 'user_profile/basic_settings.html', context)

    def post(self, request):
        user = request.user
        form = BasicSettingsFormPrivatePerson(request.POST)
        if form.is_valid():
            user = form.save(user)
            if request.FILES.__contains__("profile_picture"):
                user.profile.profile_picture = request.FILES["profile_picture"]
            user.save()
            context = self.make_context(request)
            context["is_settings_changed"] = True
            print(context)
            return render(request, 'user_profile/basic_settings.html', context)
        else:
            context = self.make_context(request)
            context['base_settings_form'] = form
            return render(request, 'user_profile/basic_settings.html', context)


class BasicSettingsPerformerView(LoginRequiredMixin, View):
    def post(self,request):
        if not request.user.isPerformer:
            return HttpResponseForbidden()
        form = BasicSettingsPerformerForm(request.POST)
        if form.is_valid():
            performer = request.user.performer
            form.save(performer)
        else:
            return HttpResponseBadRequest()
        basicSettings = BasicSettingsView()
        context = basicSettings.make_context(request)
        context["is_settings_changed"] = True
        return render(request, 'user_profile/basic_settings.html', context)
        # return HttpResponseRedirect(reverse('user_profile_app:profile'))


class PrivacySettingsView(LoginRequiredMixin, View):
    def get(self,request):
        change_password_form = ChangePasswordForm(request.user)
        data_email_and_phone = {"email":request.user.email,"phone_number":request.user.profile.phone_number}
        change_email_and_phone_form = ChangeEmailAndPhoneForm(data_email_and_phone)
        context = {"change_password_form":change_password_form,"change_email_and_phone_form":change_email_and_phone_form}
        return render(request,'user_profile/privacy_settings.html',context)
class ChangePasswordView(LoginRequiredMixin, View):
    def post(self,request):
        change_password_form = ChangePasswordForm(request.user,request.POST,instance=request.user)
        if change_password_form.is_valid():
            user = change_password_form.save()
            update_session_auth_hash(request, user)
        else:
            context = {"change_password_form": change_password_form}
            return render(request, 'user_profile/privacy_settings.html', context)
        # return HttpResponseRedirect(reverse('user_profile_app:profile'))
        change_password_form = ChangePasswordForm(request.user)
        data_email_and_phone = {"email": request.user.email, "phone_number": request.user.profile.phone_number}
        change_email_and_phone_form = ChangeEmailAndPhoneForm(data_email_and_phone)
        context = {"change_password_form": change_password_form,
                   "change_email_and_phone_form": change_email_and_phone_form,"is_password_changed":True}
        return render(request,'user_profile/privacy_settings.html',context)

class ChangeEmailAndPhoneView(LoginRequiredMixin,View):
    def post(self,request):
        change_email_and_phone_form = ChangeEmailAndPhoneForm(request.POST)
        if change_email_and_phone_form.is_valid():
            user = change_email_and_phone_form.save(request.user)
            update_session_auth_hash(request,user)
        else:
            return HttpResponseBadRequest(change_email_and_phone_form.errors)
        return HttpResponseRedirect(reverse('user_profile_app:profile'))

class ConfirmEmailView(LoginRequiredMixin,View):
    def get(self,request):
        current_site = get_current_site(request)
        email_subject = 'Approve email'
        message = render_to_string('user_profile/confirm_email.html', {
            'user': request.user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
        })
        to_email = request.user.email
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()
        return HttpResponse('We have sent link to your email address')
