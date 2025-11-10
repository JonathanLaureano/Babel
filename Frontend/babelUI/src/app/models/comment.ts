export interface Comment {
  comment_id: string;
  user: string; // User UUID
  user_username: string;
  text: string;
  content_type_display?: string;
  parent_comment: string | null;
  like_count: number;
  reply_count?: number;
  is_liked_by_user: boolean;
  replies?: Comment[];
  created_at: string;
  updated_at: string;
}

export interface CommentLike {
  like_id: string;
  comment: string;
  user: string;
  user_username: string;
  created_at: string;
}

export interface CreateCommentRequest {
  text: string;
  content_type?: string; // 'series', 'chapter', or 'user'
  object_id?: string; // UUID of the content being commented on
  parent_comment?: string; // For replies
}

export interface UpdateCommentRequest {
  text: string;
}

export interface CommentListParams {
  content_type?: string;
  object_id?: string;
  ordering?: string; // '-created_at' for newest, '-like_count' for most liked
}
