from django.urls import path

from caraauth import views

app_name = 'auth'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh/', views.JWTokenRefreshView.as_view(), name='refresh'),
]
