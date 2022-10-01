from django.urls import include, path
from rest_framework.routers import DefaultRouter

from user_area import views

app_name = 'user_area'

router = DefaultRouter()
router.register('settings', views.SettingsViewSet, basename='settings')

urlpatterns = [path('', include(router.urls))]
