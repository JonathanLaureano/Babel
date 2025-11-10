from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, CommentLikeViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'comment-likes', CommentLikeViewSet, basename='commentlike')

urlpatterns = [
    path('', include(router.urls)),
]
