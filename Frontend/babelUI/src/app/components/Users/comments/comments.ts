import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CommentService } from '../../../services/comment.service';
import { AuthService } from '../../../services/auth.service';
import { Comment, CreateCommentRequest, UpdateCommentRequest } from '../../../models/comment';
import { User } from '../../../models/user';

@Component({
  selector: 'app-comments',
  imports: [CommonModule, FormsModule],
  templateUrl: './comments.html',
  styleUrl: './comments.css',
  standalone: true,
})
export class CommentsComponent implements OnInit, OnChanges {
  @Input() contentType!: string; // 'series', 'chapter', or 'user'
  @Input() objectId!: string; // UUID of the content being commented on

  comments: Comment[] = [];
  currentUser: User | null = null;
  isLoggedIn = false;

  // UI state
  sortOrder: string = 'newest'; // 'newest' or 'most_liked'
  newCommentText: string = '';
  editingCommentId: string | null = null;
  editingCommentText: string = '';
  replyingToCommentId: string | null = null;
  replyText: string = '';
  loading = false;
  error: string | null = null;

  constructor(
    private commentService: CommentService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.isLoggedIn = !!user;
    });
    
    this.loadComments();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['contentType'] || changes['objectId']) {
      this.loadComments();
    }
  }

  loadComments(): void {
    if (!this.contentType || !this.objectId) {
      return;
    }

    this.loading = true;
    this.error = null;

    const ordering = this.sortOrder === 'newest' ? '-created_at' : '-like_count';
    
    this.commentService.getCommentsByContent({
      content_type: this.contentType,
      object_id: this.objectId,
      ordering: ordering
    }).subscribe({
      next: (comments) => {
        this.comments = comments;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading comments:', err);
        this.error = 'Failed to load comments';
        this.loading = false;
      }
    });
  }

  onSortChange(): void {
    this.loadComments();
  }

  get commentCount(): number {
    return this.comments.length;
  }

  canEditComment(comment: Comment): boolean {
    return this.isLoggedIn && this.currentUser?.user_id === comment.user;
  }

  canDeleteComment(comment: Comment): boolean {
    return this.isLoggedIn && 
      (this.currentUser?.user_id === comment.user || this.currentUser?.is_staff === true);
  }

  createComment(): void {
    if (!this.isLoggedIn) {
      this.error = 'You must be logged in to comment';
      return;
    }

    if (!this.newCommentText.trim()) {
      return;
    }

    const commentData: CreateCommentRequest = {
      text: this.newCommentText.trim(),
      content_type: this.contentType,
      object_id: this.objectId
    };

    this.commentService.createComment(commentData).subscribe({
      next: (comment) => {
        // Ensure like_count is initialized
        if (comment.like_count === undefined || comment.like_count === null) {
          comment.like_count = 0;
        }
        this.comments.unshift(comment);
        this.newCommentText = '';
        this.error = null;
      },
      error: (err) => {
        console.error('Error creating comment:', err);
        this.error = 'Failed to create comment';
      }
    });
  }

  startEdit(comment: Comment): void {
    this.editingCommentId = comment.comment_id;
    this.editingCommentText = comment.text;
    this.replyingToCommentId = null; // Close reply form if open
  }

  cancelEdit(): void {
    this.editingCommentId = null;
    this.editingCommentText = '';
  }

  saveEdit(commentId: string): void {
    if (!this.editingCommentText.trim()) {
      return;
    }

    const updateData: UpdateCommentRequest = {
      text: this.editingCommentText.trim()
    };

    this.commentService.updateComment(commentId, updateData).subscribe({
      next: (updatedComment) => {
        const index = this.comments.findIndex(c => c.comment_id === commentId);
        if (index !== -1) {
          this.comments[index] = updatedComment;
        }
        this.cancelEdit();
        this.error = null;
      },
      error: (err) => {
        console.error('Error updating comment:', err);
        this.error = 'Failed to update comment';
      }
    });
  }

  deleteComment(commentId: string): void {
    if (!confirm('Are you sure you want to delete this comment?')) {
      return;
    }

    this.commentService.deleteComment(commentId).subscribe({
      next: () => {
        this.comments = this.comments.filter(c => c.comment_id !== commentId);
        this.error = null;
      },
      error: (err) => {
        console.error('Error deleting comment:', err);
        this.error = 'Failed to delete comment';
      }
    });
  }

  toggleLike(comment: Comment): void {
    if (!this.isLoggedIn) {
      this.error = 'You must be logged in to like comments';
      return;
    }

    if (comment.is_liked_by_user) {
      this.commentService.unlikeComment(comment.comment_id).subscribe({
        next: () => {
          comment.is_liked_by_user = false;
          comment.like_count = (comment.like_count || 0) - 1;
          this.error = null;
        },
        error: (err) => {
          console.error('Error unliking comment:', err);
          this.error = 'Failed to unlike comment';
        }
      });
    } else {
      this.commentService.likeComment(comment.comment_id).subscribe({
        next: () => {
          comment.is_liked_by_user = true;
          comment.like_count = (comment.like_count || 0) + 1;
          this.error = null;
        },
        error: (err) => {
          console.error('Error liking comment:', err);
          this.error = 'Failed to like comment';
        }
      });
    }
  }

  startReply(commentId: string): void {
    this.replyingToCommentId = commentId;
    this.replyText = '';
    this.editingCommentId = null; // Close edit form if open
  }

  cancelReply(): void {
    this.replyingToCommentId = null;
    this.replyText = '';
  }

  createReply(parentCommentId: string): void {
    if (!this.isLoggedIn) {
      this.error = 'You must be logged in to reply';
      return;
    }

    if (!this.replyText.trim()) {
      return;
    }

    const replyData: CreateCommentRequest = {
      text: this.replyText.trim(),
      parent_comment: parentCommentId
    };

    this.commentService.createComment(replyData).subscribe({
      next: (reply) => {
        // Ensure like_count is initialized
        if (reply.like_count === undefined || reply.like_count === null) {
          reply.like_count = 0;
        }
        const parentComment = this.comments.find(c => c.comment_id === parentCommentId);
        if (parentComment) {
          if (!parentComment.replies) {
            parentComment.replies = [];
          }
          parentComment.replies.push(reply);
          if (parentComment.reply_count !== undefined) {
            parentComment.reply_count++;
          }
        }
        this.cancelReply();
        this.error = null;
      },
      error: (err) => {
        console.error('Error creating reply:', err);
        this.error = 'Failed to create reply';
      }
    });
  }

  getTimeSince(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    const intervals = [
      { label: 'year', seconds: 31536000 },
      { label: 'month', seconds: 2592000 },
      { label: 'week', seconds: 604800 },
      { label: 'day', seconds: 86400 },
      { label: 'hour', seconds: 3600 },
      { label: 'minute', seconds: 60 },
      { label: 'second', seconds: 1 }
    ];

    for (const interval of intervals) {
      const count = Math.floor(seconds / interval.seconds);
      if (count >= 1) {
        return `${count} ${interval.label}${count !== 1 ? 's' : ''} ago`;
      }
    }

    return 'just now';
  }
}
