from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from caraauth.serializers import UserProfileSerializer


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'user_area/dashboard.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_area/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile_form'] = UserProfileSerializer()
        return context
