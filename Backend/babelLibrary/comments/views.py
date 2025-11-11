from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from .models import Comment, CommentLike
from .serializers import (
    CommentSerializer, CommentCreateUpdateSerializer, 
    CommentLikeSerializer, CommentReplySerializer
)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Comment instances.
    Supports full CRUD operations, nested replies, and filtering by content type.
    """
    queryset = Comment.objects.all().select_related('user', 'parent_comment', 'content_type').prefetch_related('likes')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'parent_comment']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Conditionally prefetch 'replies' only for actions that display nested comments.
        This optimizes query performance by avoiding unnecessary prefetching.
        For by_user action, we need to prefetch the generic relation content objects.
        """
        qs = super().get_queryset()
        # Only prefetch replies when displaying top-level comments with nested replies
        if self.action in ['list', 'by_content', 'retrieve']:
            return qs.prefetch_related('replies__user', 'replies__likes')
        elif self.action == 'by_user':
            # For by_user, prefetch the related Series and Chapter objects to avoid N+1 queries
            # We can't directly prefetch generic relations, but we can use prefetch_related_objects in the view
            return qs
        return qs
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateUpdateSerializer
        return CommentSerializer
    
    def get_permissions(self):
        """
        Allow anonymous users to read comments.
        Require authentication for create, update, delete.
        """
        if self.action in ['list', 'retrieve', 'by_content', 'replies']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Automatically set the user to the authenticated user."""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Only allow users to update their own comments."""
        comment = self.get_object()
        if comment.user != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own comments.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only allow users to delete their own comments."""
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only delete your own comments.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def by_content(self, request):
        """
        Get comments for a specific content object (Series, Chapter, or User).
        Query params: content_type (series/chapter/user), object_id (UUID)
        """
        content_type_str = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        
        if not content_type_str or not object_id:
            return Response(
                {'error': 'content_type and object_id parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the ContentType object
        try:
            if content_type_str.lower() == 'series':
                content_type = ContentType.objects.get(app_label='library', model='series')
            elif content_type_str.lower() == 'chapter':
                content_type = ContentType.objects.get(app_label='library', model='chapter')
            elif content_type_str.lower() == 'user':
                content_type = ContentType.objects.get(app_label='users', model='user')
            else:
                return Response(
                    {'error': 'content_type must be one of: series, chapter, user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ContentType.DoesNotExist:
            return Response(
                {'error': f'Invalid content type: {content_type_str}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter comments by content type and object ID, excluding replies (parent_comment=None)
        comments = self.queryset.filter(
            content_type=content_type,
            object_id=object_id,
            parent_comment=None  # Only get top-level comments
        )

        # Apply ordering if specified in query params
        ordering = request.query_params.get('ordering')
        allowed_ordering_fields = getattr(self, 'ordering_fields', ['created_at', 'like_count'])
        if ordering:
            # Support comma-separated ordering fields, as in DRF
            ordering_fields = [field.strip() for field in ordering.split(',')]
            # Only allow ordering by allowed fields
            valid_fields = []
            for field in ordering_fields:
                field_name = field.lstrip('-')
                if field_name in allowed_ordering_fields:
                    valid_fields.append(field)
            if valid_fields:
                comments = comments.order_by(*valid_fields)

        # Apply pagination
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a comment. Requires authentication."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to like a comment'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comment = self.get_object()
        
        # Check if user has already liked
        existing_like = CommentLike.objects.filter(
            comment=comment,
            user=request.user
        ).first()
        
        if existing_like:
            return Response(
                {'error': 'You have already liked this comment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new like
        like = CommentLike.objects.create(
            comment=comment,
            user=request.user
        )
        
        serializer = CommentLikeSerializer(like, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        """Unlike a comment. Requires authentication."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to unlike a comment'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comment = self.get_object()
        
        # Check if user has liked
        existing_like = CommentLike.objects.filter(
            comment=comment,
            user=request.user
        ).first()
        
        if not existing_like:
            return Response(
                {'error': 'You have not liked this comment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete the like
        existing_like.delete()
        
        return Response(
            {'message': 'Comment unliked successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Get all replies to a specific comment."""
        comment = self.get_object()
        replies = comment.replies.all()
        
        # Apply pagination
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = CommentReplySerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentReplySerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """
        Get all comments by a specific user.
        Query params: user (user_id)
        """
        user_id = request.query_params.get('user')
        
        if not user_id:
            return Response(
                {'error': 'user parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter comments by user
        comments = self.get_queryset().filter(user__user_id=user_id)
        
        # Apply ordering if specified in query params
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering:
            comments = comments.order_by(ordering)
        
        # Apply pagination
        page = self.paginate_queryset(comments)
        if page is not None:
            # Prefetch generic relation objects to avoid N+1 queries
            self._prefetch_content_objects(page)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # For non-paginated results
        comments_list = list(comments)
        self._prefetch_content_objects(comments_list)
        serializer = self.get_serializer(comments_list, many=True)
        return Response(serializer.data)
    
    def _prefetch_content_objects(self, comments):
        """
        Manually prefetch generic relation content objects (Series/Chapter) to avoid N+1 queries.
        This groups comments by content type and bulk fetches the related objects.
        """
        from library.models import Series, Chapter
        from collections import defaultdict
        
        # Group comments by content type
        series_ids = []
        chapter_ids = []
        
        for comment in comments:
            if comment.content_type.model == 'series':
                series_ids.append(comment.object_id)
            elif comment.content_type.model == 'chapter':
                chapter_ids.append(comment.object_id)
        
        # Bulk fetch Series and Chapter objects
        series_map = {}
        chapter_map = {}
        
        if series_ids:
            series_objs = Series.objects.filter(series_id__in=series_ids)
            series_map = {str(s.series_id): s for s in series_objs}
        
        if chapter_ids:
            # Use select_related to also fetch the related series for chapters
            chapter_objs = Chapter.objects.filter(chapter_id__in=chapter_ids).select_related('series')
            chapter_map = {str(c.chapter_id): c for c in chapter_objs}
        
        # Cache the content objects on each comment instance
        for comment in comments:
            if comment.content_type.model == 'series':
                comment._cached_content_object = series_map.get(str(comment.object_id))
            elif comment.content_type.model == 'chapter':
                comment._cached_content_object = chapter_map.get(str(comment.object_id))


class CommentLikeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing CommentLike instances.
    Read-only because likes are created/deleted via CommentViewSet actions.
    """
    queryset = CommentLike.objects.all().select_related('user', 'comment')
    serializer_class = CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['comment', 'user']
