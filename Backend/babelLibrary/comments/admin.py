from django.contrib import admin
from .models import Comment, CommentLike


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment_id', 'user', 'text_preview', 'content_type', 'parent_comment', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['text', 'user__username']
    readonly_fields = ['comment_id', 'created_at', 'updated_at', 'like_count', 'reply_count']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['like_id', 'comment', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'comment__text']
    readonly_fields = ['like_id', 'created_at']
