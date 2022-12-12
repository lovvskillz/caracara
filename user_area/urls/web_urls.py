from django.urls import path

from user_area.views.web import user

app_name = 'user_area'

urlpatterns = [
    path('dashboard/', user.DashboardView.as_view(), name='dashboard'),
]
