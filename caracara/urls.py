from django.contrib import admin
from django.urls import include, path

api_urlpatterns = [
    path('auth/', include('caraauth.urls_api')),
    path('user/', include('user_area.urls_api')),
]

urlpatterns = [path('admin/', admin.site.urls), path('api/', include(api_urlpatterns))]
