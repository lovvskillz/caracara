from django.urls import path

from caraauth import views

app_name = 'auth_api'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh/', views.TokenRefreshView.as_view(), name='refresh'),
]
