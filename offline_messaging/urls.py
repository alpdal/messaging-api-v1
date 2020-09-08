from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from .custom_authtoken import custom_token_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('auth/', custom_token_view),
]
