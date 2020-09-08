from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import UserViewSet, MessageViewSet, BlockViewSet

router = routers.DefaultRouter()
router.register('user', UserViewSet)
router.register('message', MessageViewSet, basename='message-list')
router.register('block', BlockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
