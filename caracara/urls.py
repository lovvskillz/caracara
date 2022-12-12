from django.contrib import admin
from django.urls import include, path

api_urlpatterns = (
    [
        path('auth/', include('caraauth.urls.api_urls')),
        path('user/', include('user_area.urls.api_urls')),
    ],
    'api',
)

web_urlpatterns = (
    [
        path('auth/', include('caraauth.urls.web_urls')),
        path('user/', include('user_area.urls.web_urls')),
    ],
    'web',
)

urlpatterns = [
    path('', include(web_urlpatterns)),
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
]
