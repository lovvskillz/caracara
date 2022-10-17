from django.urls import include, path

from user_area.views import settings, twofa

app_name = 'user_area'

twofa_urlpatterns = [path('setup/', twofa.Setup2FAView.as_view(), name='setup_2fa')]

urlpatterns = [
    path('profile/', settings.UserProfileView.as_view(), name='profile'),
    path('2fa/', include(twofa_urlpatterns)),
]
