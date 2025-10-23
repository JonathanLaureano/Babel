from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NovelViewSet, ChapterViewSet

router = DefaultRouter()
router.register(r'novels', NovelViewSet)
router.register(r'chapters', ChapterViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
