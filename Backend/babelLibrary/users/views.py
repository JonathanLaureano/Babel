from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .models import Role, Permission, RolePermission, User, Bookmark, ReadingHistory
from .serializers import (
    RoleSerializer, PermissionSerializer, RolePermissionSerializer, 
    UserSerializer, BookmarkSerializer, ReadingHistorySerializer
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Standalone login endpoint that returns JWT tokens"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'detail': 'Account is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    refresh = RefreshToken.for_user(user)
    user_data = UserSerializer(user).data

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': user_data
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_login_view(request):
    """Google OAuth login endpoint"""
    token = request.data.get('token')
    
    if not token:
        return Response(
            {'detail': 'Google token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        # Get user info from Google token
        email = idinfo.get('email')
        
        if not email:
            return Response(
                {'detail': 'Email not provided by Google'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'No account found with this email. Please register first.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not user.is_active:
            return Response(
                {'detail': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        })
        
    except ValueError as e:
        # Invalid token
        return Response(
            {'detail': f'Invalid Google token: {str(e)}'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'detail': f'Authentication failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_register_view(request):
    """Google OAuth registration endpoint"""
    token = request.data.get('token')
    
    if not token:
        return Response(
            {'detail': 'Google token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        # Get user info from Google token
        email = idinfo.get('email')
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')
        name = idinfo.get('name', '')
        
        if not email:
            return Response(
                {'detail': 'Email not provided by Google'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'detail': 'An account with this email already exists. Please login instead.'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Generate username from email or name
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        
        # Ensure username is unique
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Get or create default 'Reader' role
        reader_role, _ = Role.objects.get_or_create(
            name='Reader',
            defaults={'description': 'Default reader role'}
        )
        
        # Create new user (no password needed for Google OAuth users)
        user = User.objects.create(
            username=username,
            email=email,
            role=reader_role,
            is_active=True
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        # Invalid token
        return Response(
            {'detail': f'Invalid Google token: {str(e)}'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'detail': f'Registration failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing User instances.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated] # Default to authenticated
    lookup_field = 'user_id'

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        - 'list' action (GET all users) is restricted to staff members.
        - 'create' action (registration) is open to any user.
        - Other actions default to requiring authentication.
        """
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Override create to assign default reader role"""
        data = request.data.copy()

        # Get or create default 'Reader' role if not specified
        if 'role' not in data:
            reader_role, _ = Role.objects.get_or_create(
                name='Reader',
                defaults={'description': 'Default reader role'}
            )
            data['role'] = str(reader_role.role_id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Generate JWT tokens for the newly created user
        user = serializer.instance
        refresh = RefreshToken.for_user(user)

        # Return user data along with authentication tokens
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    # This will handle PUT requests to /api/users/{user_id}/
    def update(self, request, *args, **kwargs):
        """Update user profile (PUT)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)

    # This will handle PATCH requests to /api/users/{user_id}/
    def partial_update(self, request, *args, **kwargs):
        """Partial update user profile (PATCH)"""
        instance = self.get_object()
        # Ensure a user can only update their own profile
        if instance != request.user and not request.user.is_staff:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete user account (DELETE)"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """Login endpoint that returns JWT tokens"""
        return login_view(request)

    @action(detail=True, methods=['post'])
    def set_password(self, request, user_id=None):
        """Set a new password for the user"""
        user = self.get_object()
        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
            return Response({'status': 'password set'})
        return Response({'error': 'password field is required'}, status=400)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, user_id=None):
        """Deactivate a user account"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})

    @action(detail=True, methods=['post'])
    def activate(self, request, user_id=None):
        """Activate a user account"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Role instances.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'role_id'

    def list(self, request, *args, **kwargs):
        """
        Ensure the default 'Reader' role exists before listing roles.
        """
        Role.objects.get_or_create(name='Reader', defaults={'description': 'Default role with read-only access.'})
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def users(self, request, role_id=None):
        """Get all users with this role"""
        role = self.get_object()
        users = role.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def permissions(self, request, role_id=None):
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
    lookup_field = 'permission_id'  # Use permission_id instead of pk in URLs


class RolePermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Role-Permission relationships.
    """
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookmarkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user bookmarks.
    """
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'bookmark_id'

    def get_queryset(self):
        """Return bookmarks filtered by query parameters."""
        queryset = Bookmark.objects.select_related('user', 'series').all()
        
        # Filter by user if specified in query params
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user__user_id=user_id)
        
        # Filter by series if specified in query params
        series_id = self.request.query_params.get('series', None)
        if series_id:
            queryset = queryset.filter(series__series_id=series_id)
        
        return queryset

    def perform_create(self, serializer):
        """Automatically set the user to the current authenticated user."""
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Allow users to delete their own bookmarks."""
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not have permission to delete this bookmark.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class ReadingHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reading history.
    """
    serializer_class = ReadingHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'history_id'
    http_method_names = ['get', 'post', 'head', 'options']  # Only allow GET and POST

    def get_queryset(self):
        """Return reading history filtered by query parameters."""
        queryset = ReadingHistory.objects.select_related(
            'user', 'series', 'chapter'
        ).all()
        
        # Filter by user if specified in query params
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user__user_id=user_id)
        
        # Filter by series if specified in query params
        series_id = self.request.query_params.get('series', None)
        if series_id:
            queryset = queryset.filter(series__series_id=series_id)
        
        # Support ordering
        ordering = self.request.query_params.get('ordering', '-last_read_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset

    def perform_create(self, serializer):
        """Automatically set the user to the current authenticated user."""
        serializer.save(user=self.request.user)
