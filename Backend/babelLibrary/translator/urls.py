"""
URL configuration for translator app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TranslationJobViewSet

router = DefaultRouter()
router.register(r'jobs', TranslationJobViewSet, basename='translationjob')

urlpatterns = [
    path('', include(router.urls)),
]
