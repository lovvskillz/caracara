from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from caraauth.forms import RegisterForm, LoginForm
from caraauth.permissions import AnonymousRequiredMixin


class LoginView(AnonymousRequiredMixin, TemplateView):
    template_name = 'caraauth/login.html'

    def get(self, request, *args, **kwargs):
        data = {'login_form': LoginForm()}
        return render(request, self.template_name, context=data)

    def post(self, request, *args, **kwargs):
        serializer = LoginForm(data=request.POST)
        if serializer.is_valid():
            user = serializer.cleaned_data.get('user')
            login(request, user)
            return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))
        if errors := serializer.errors.get('non_field_errors'):
            for error in errors:
                messages.error(request, str(error))
        else:
            messages.error(request, _("Login could not be performed."))
        data = {'login_form': serializer}
        return render(request, self.template_name, context=data)


class RegisterView(AnonymousRequiredMixin, TemplateView):
    template_name = 'caraauth/register.html'

    def get(self, request, *args, **kwargs):
        data = {'register_form': RegisterForm()}
        return render(request, self.template_name, context=data)

    def post(self, request, *args, **kwargs):
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.create_user()
            login(request, user)
            return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))
        messages.error(request, _("New account could not be created."))
        data = {'register_form': form}
        return render(request, self.template_name, context=data)
