from django.urls import path

from caraauth.views import web_views

app_name = 'auth_web'
urlpatterns = [
    path('register/', web_views.RegisterView.as_view(), name='register'),
    path('login/', web_views.LoginView.as_view(), name='login'),
]
