import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Comment, CommentLike, CreateCommentRequest, UpdateCommentRequest, CommentListParams } from '../models/comment';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root'
})
export class CommentService {
  private apiUrl = 'http://localhost:8000/api/comments';

  constructor(private http: HttpClient) { }

  // Get comments by content (series, chapter, or user)
  getCommentsByContent(params: CommentListParams): Observable<Comment[]> {
    let httpParams = new HttpParams();
    
    if (params.content_type) {
      httpParams = httpParams.set('content_type', params.content_type);
    }
    if (params.object_id) {
      httpParams = httpParams.set('object_id', params.object_id);
    }
    if (params.ordering) {
      httpParams = httpParams.set('ordering', params.ordering);
    }

    return this.http.get<PaginatedResponse<Comment>>(`${this.apiUrl}/by_content/`, { params: httpParams })
      .pipe(
        map(response => response.results || [])
      );
  }

  // Get a single comment
  getComment(commentId: string): Observable<Comment> {
    return this.http.get<Comment>(`${this.apiUrl}/${commentId}/`);
  }

  // Create a new comment
  createComment(commentData: CreateCommentRequest): Observable<Comment> {
    return this.http.post<Comment>(`${this.apiUrl}/`, commentData);
  }

  // Update a comment (only text can be updated)
  updateComment(commentId: string, commentData: UpdateCommentRequest): Observable<Comment> {
    return this.http.patch<Comment>(`${this.apiUrl}/${commentId}/`, commentData);
  }

  // Delete a comment
  deleteComment(commentId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${commentId}/`);
  }

  // Like a comment
  likeComment(commentId: string): Observable<CommentLike> {
    return this.http.post<CommentLike>(`${this.apiUrl}/${commentId}/like/`, {});
  }

  // Unlike a comment
  unlikeComment(commentId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${commentId}/unlike/`);
  }

  // Get replies to a comment
  getReplies(commentId: string): Observable<Comment[]> {
    return this.http.get<PaginatedResponse<Comment>>(`${this.apiUrl}/${commentId}/replies/`)
      .pipe(
        map(response => response.results || [])
      );
  }
}
