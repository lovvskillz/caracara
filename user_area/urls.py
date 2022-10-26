from django.urls import include, path

from user_area.views import settings, twofa

app_name = 'user_area'

twofa_urlpatterns = [
    path('setup/', twofa.Setup2FAView.as_view(), name='2fa_setup'),
    path('backup-tokens/', twofa.BackupTokensView.as_view(), name='2fa_static_tokens'),
    path(
        'refresh-tokens/',
        twofa.RefreshBackupTokensView.as_view(),
        name='2fa_refresh_static_tokens',
    ),
    path('disable/', twofa.Disable2FAView.as_view(), name='2fa_disable'),
]

urlpatterns = [
    path('profile/', settings.UserProfileView.as_view(), name='profile'),
    path('2fa/', include(twofa_urlpatterns)),
]
