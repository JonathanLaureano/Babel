import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Series } from '../models/series';
import { Chapter, ChapterListItem } from '../models/chapter';
import { Genre } from '../models/genre';

@Injectable({
  providedIn: 'root'
})
export class LibraryService {
  private apiUrl = 'http://localhost:8000/api/library';

  constructor(private http: HttpClient) { }

  // Series endpoints
  getSeries(searchQuery?: string): Observable<Series[]> {
    let params = new HttpParams();
    if (searchQuery) {
      params = params.set('search', searchQuery);
    }
    return this.http.get<Series[]>(`${this.apiUrl}/series/`, { params });
  }

  getSeriesById(id: string): Observable<Series> {
    return this.http.get<Series>(`${this.apiUrl}/series/${id}/`);
  }

  createSeries(seriesData: any): Observable<Series> {
    return this.http.post<Series>(`${this.apiUrl}/series/`, seriesData);
  }

  updateSeries(id: string, seriesData: any): Observable<Series> {
    return this.http.patch<Series>(`${this.apiUrl}/series/${id}/`, seriesData);
  }

  deleteSeries(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/series/${id}/`);
  }

  getSeriesChapters(seriesId: string): Observable<ChapterListItem[]> {
    return this.http.get<ChapterListItem[]>(`${this.apiUrl}/series/${seriesId}/chapters/`);
  }

  // Chapter endpoints
  getChapter(id: string): Observable<Chapter> {
    return this.http.get<Chapter>(`${this.apiUrl}/chapters/${id}/`);
  }

  createChapter(chapterData: any): Observable<Chapter> {
    return this.http.post<Chapter>(`${this.apiUrl}/chapters/`, chapterData);
  }

  updateChapter(id: string, chapterData: any): Observable<Chapter> {
    return this.http.patch<Chapter>(`${this.apiUrl}/chapters/${id}/`, chapterData);
  }

  deleteChapter(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/chapters/${id}/`);
  }

  getNextChapter(id: string): Observable<Chapter> {
    return this.http.get<Chapter>(`${this.apiUrl}/chapters/${id}/next/`);
  }

  getPreviousChapter(id: string): Observable<Chapter> {
    return this.http.get<Chapter>(`${this.apiUrl}/chapters/${id}/previous/`);
  }

  // Genre endpoints
  getGenres(): Observable<Genre[]> {
    return this.http.get<Genre[]>(`${this.apiUrl}/genres/`);
  }

  // Rating endpoint
  rateSeriesRating(seriesId: string, rating: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/series/${seriesId}/rate/`, { rating });
  }

  // View tracking endpoints
  trackSeriesView(seriesId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/series/${seriesId}/track_view/`, {});
  }

  trackChapterView(chapterId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/chapters/${chapterId}/track_view/`, {});
  }
}
