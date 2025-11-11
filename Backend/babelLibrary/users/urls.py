from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet, PermissionViewSet, RolePermissionViewSet, 
    UserViewSet, BookmarkViewSet, ReadingHistoryViewSet
)

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'role-permissions', RolePermissionViewSet, basename='rolepermission')
router.register(r'users', UserViewSet, basename='user')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
router.register(r'reading-history', ReadingHistoryViewSet, basename='reading-history')

# The only thing this file should export is the router's URLs.
urlpatterns = [
    path('', include(router.urls)),
]
