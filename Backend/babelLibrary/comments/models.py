import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    """Stores comments that can be attached to Series, Chapters, or Users, and can reply to other comments."""
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    
    # Generic foreign key to allow comments on Series, Chapter, or User
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Self-referential relationship for nested comments (replies)
    parent_comment = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['parent_comment']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        try:
            content_display = self.content_object if self.content_object else f"{self.content_type.model}:{self.object_id}"
            return f"Comment by {self.user.username} on {content_display}"
        except Exception:
            # Fallback if content_object is deleted or causes an error
            return f"Comment by {self.user.username} on {self.content_type.model}:{self.object_id}"
    
    @property
    def like_count(self):
        """Get total likes for this comment."""
        return self.likes.count()
    
    @property
    def reply_count(self):
        """Get total replies to this comment."""
        return self.replies.count()


class CommentLike(models.Model):
    """Stores likes on comments. A user can only like a comment once."""
    like_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'commentlike'
        unique_together = ('comment', 'user')
        indexes = [
            models.Index(fields=['comment', 'user']),
        ]
    
    def __str__(self):
        try:
            return f"{self.user.username} likes comment {self.comment.comment_id}"
        except Exception:
            # Fallback if user or comment is deleted or causes an error
            return f"CommentLike {self.like_id}"
