from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, SeriesViewSet, SeriesGenreViewSet, ChapterViewSet

router = DefaultRouter()
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'series', SeriesViewSet, basename='series')
router.register(r'series-genres', SeriesGenreViewSet, basename='seriesgenre')
router.register(r'chapters', ChapterViewSet, basename='chapter')

urlpatterns = [
    path('', include(router.urls)),
]
