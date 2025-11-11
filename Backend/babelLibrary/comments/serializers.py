from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Comment, CommentLike


class CommentLikeSerializer(serializers.ModelSerializer):
    """Serializer for comment likes."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['like_id', 'comment', 'user', 'user_username', 'created_at']
        read_only_fields = ['like_id', 'user', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments with nested replies."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    # Fields for generic foreign key (write_only fields not required since this serializer is for reading)
    content_type = serializers.CharField(write_only=True, required=False)
    object_id = serializers.UUIDField(write_only=True, required=False)
    content_type_display = serializers.SerializerMethodField(read_only=True)
    
    # Additional fields for navigation context
    series_id = serializers.SerializerMethodField(read_only=True)
    series_title = serializers.SerializerMethodField(read_only=True)
    chapter_id = serializers.SerializerMethodField(read_only=True)
    chapter_title = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'comment_id', 'user', 'user_username', 'text', 
            'content_type', 'object_id', 'content_type_display',
            'parent_comment', 'like_count', 'reply_count', 
            'is_liked_by_user', 'replies', 'created_at', 'updated_at',
            'series_id', 'series_title', 'chapter_id', 'chapter_title'
        ]
        read_only_fields = ['comment_id', 'user', 'like_count', 'reply_count', 'created_at', 'updated_at']
    
    def get_content_type_display(self, obj):
        """Return a human-readable content type."""
        return obj.content_type.model
    
    def get_series_id(self, obj):
        """Get the series ID from the content object."""
        if obj.content_type.model == 'series':
            return str(obj.object_id)
        elif obj.content_type.model == 'chapter':
            try:
                from library.models import Chapter
                chapter = Chapter.objects.get(chapter_id=obj.object_id)
                return str(chapter.series.series_id)
            except:
                return None
        return None
    
    def get_series_title(self, obj):
        """Get the series title from the content object."""
        if obj.content_type.model == 'series':
            try:
                from library.models import Series
                series = Series.objects.get(series_id=obj.object_id)
                return series.title
            except:
                return None
        elif obj.content_type.model == 'chapter':
            try:
                from library.models import Chapter
                chapter = Chapter.objects.get(chapter_id=obj.object_id)
                return chapter.series.title
            except:
                return None
        return None
    
    def get_chapter_id(self, obj):
        """Get the chapter ID if the comment is on a chapter."""
        if obj.content_type.model == 'chapter':
            return str(obj.object_id)
        return None
    
    def get_chapter_title(self, obj):
        """Get the chapter number if the comment is on a chapter."""
        if obj.content_type.model == 'chapter':
            try:
                from library.models import Chapter
                chapter = Chapter.objects.get(chapter_id=obj.object_id)
                return str(chapter.chapter_number)
            except:
                return None
        return None
    
    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_replies(self, obj):
        """Get nested replies (only one level deep to avoid infinite recursion)."""
        if obj.parent_comment is None:
            replies = obj.replies.all()
            return CommentReplySerializer(replies, many=True, context=self.context).data
        return []


class CommentReplySerializer(serializers.ModelSerializer):
    """Simplified serializer for nested comment replies (no further nesting)."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'comment_id', 'user', 'user_username', 'text', 
            'parent_comment', 'like_count', 'is_liked_by_user', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['comment_id', 'user', 'like_count', 'created_at', 'updated_at']
    
    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating comments."""
    content_type = serializers.CharField(write_only=True, required=False)
    object_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Comment
        fields = ['comment_id', 'text', 'content_type', 'object_id', 'parent_comment']
        read_only_fields = ['comment_id']
    
    def validate_content_type(self, value):
        """Validate that the content type is one of the allowed models."""
        allowed_models = ['series', 'chapter', 'user']
        if value.lower() not in allowed_models:
            raise serializers.ValidationError(
                f"Content type must be one of: {', '.join(allowed_models)}"
            )
        return value.lower()
    
    def create(self, validated_data):
        """Override create to handle content type lookup."""
        content_type_str = validated_data.pop('content_type', None)
        object_id = validated_data.pop('object_id', None)
        parent_comment = validated_data.get('parent_comment')
        
        # If this is a reply, inherit content_type and object_id from parent
        if parent_comment and not (content_type_str and object_id):
            validated_data['content_type'] = parent_comment.content_type
            validated_data['object_id'] = parent_comment.object_id
        elif content_type_str and object_id:
            # Get the ContentType object based on the model name
            content_type = None
            try:
                if content_type_str == 'series':
                    content_type = ContentType.objects.get(app_label='library', model='series')
                elif content_type_str == 'chapter':
                    content_type = ContentType.objects.get(app_label='library', model='chapter')
                elif content_type_str == 'user':
                    content_type = ContentType.objects.get(app_label='users', model='user')
                else:
                    raise serializers.ValidationError(f"Invalid content type: {content_type_str}")
            except ContentType.DoesNotExist:
                raise serializers.ValidationError(f"Content type not found: {content_type_str}")
            
            validated_data['content_type'] = content_type
            validated_data['object_id'] = object_id
        else:
            raise serializers.ValidationError(
                "Either provide content_type and object_id, or parent_comment for replies"
            )
        
        return super().create(validated_data)
