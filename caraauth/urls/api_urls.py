from django.urls import path

from caraauth.views import api_views

app_name = 'auth_api'
urlpatterns = [
    path('register/', api_views.RegisterView.as_view(), name='register'),
    path('login/', api_views.LoginView.as_view(), name='login'),
    path('refresh/', api_views.TokenRefreshView.as_view(), name='refresh'),
]
