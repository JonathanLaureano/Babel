import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { 
  Bookmark, 
  ReadingHistory, 
  UserComment, 
  CreateBookmarkRequest,
  UpdateReadingHistoryRequest 
} from '../models/user-data';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root'
})
export class UserDataService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  // Bookmark endpoints
  getUserBookmarks(userId: string): Observable<Bookmark[]> {
    return this.http.get<PaginatedResponse<Bookmark>>(`${this.apiUrl}/bookmarks/?user=${userId}`)
      .pipe(
        map(response => response.results || [])
      );
  }

  createBookmark(bookmarkData: CreateBookmarkRequest): Observable<Bookmark> {
    return this.http.post<Bookmark>(`${this.apiUrl}/bookmarks/`, bookmarkData);
  }

  deleteBookmark(bookmarkId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/bookmarks/${bookmarkId}/`);
  }

  checkBookmarkExists(userId: string, seriesId: string): Observable<Bookmark | null> {
    return this.http.get<PaginatedResponse<Bookmark>>(`${this.apiUrl}/bookmarks/?user=${userId}&series=${seriesId}`)
      .pipe(
        map(response => response.results && response.results.length > 0 ? response.results[0] : null)
      );
  }

  // Reading history endpoints
  getUserReadingHistory(userId: string): Observable<ReadingHistory[]> {
    return this.http.get<PaginatedResponse<ReadingHistory>>(`${this.apiUrl}/reading-history/?user=${userId}&ordering=-last_read_at`)
      .pipe(
        map(response => response.results || [])
      );
  }

  getSeriesReadingHistory(userId: string, seriesId: string): Observable<ReadingHistory | null> {
    return this.http.get<PaginatedResponse<ReadingHistory>>(`${this.apiUrl}/reading-history/?user=${userId}&series=${seriesId}`)
      .pipe(
        map(response => response.results && response.results.length > 0 ? response.results[0] : null)
      );
  }

  updateReadingHistory(historyData: UpdateReadingHistoryRequest): Observable<ReadingHistory> {
    return this.http.post<ReadingHistory>(`${this.apiUrl}/reading-history/`, historyData);
  }

  // User comments endpoint
  getUserComments(userId: string): Observable<UserComment[]> {
    return this.http.get<PaginatedResponse<UserComment>>(`${this.apiUrl}/comments/by_user/?user=${userId}&ordering=-created_at`)
      .pipe(
        map(response => response.results || [])
      );
  }
}
