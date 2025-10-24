from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Role, Permission, RolePermission, User
from .serializers import RoleSerializer, PermissionSerializer, RolePermissionSerializer, UserSerializer


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Role instances.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users with this role"""
        role = self.get_object()
        users = role.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get all permissions for this role"""
        role = self.get_object()
        role_permissions = role.role_permissions.all()
        permissions_list = [rp.permission for rp in role_permissions]
        serializer = PermissionSerializer(permissions_list, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Permission instances.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RolePermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Role-Permission relationships.
    """
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing User instances.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """Set a new password for the user"""
        user = self.get_object()
        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
            return Response({'status': 'password set'})
        return Response({'error': 'password field is required'}, status=400)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user account"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user account"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})
