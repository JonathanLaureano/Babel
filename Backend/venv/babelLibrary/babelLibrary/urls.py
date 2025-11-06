"""
URL configuration for the babelLibrary project.
"""
from django.contrib import admin
from django.urls import path, include
from users.views import login_view  # Import login_view here

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/users/login/', login_view, name='login'), # Add the login path here
    path('api/', include('users.urls')),
    path('api/library/', include('library.urls')),
]
