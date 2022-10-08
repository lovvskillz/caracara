from django.urls import path

from user_area import views

app_name = 'user_area'

urlpatterns = [path('profile', views.UserProfileView.as_view(), name='profile')]
