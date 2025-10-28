import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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
  getSeries(): Observable<Series[]> {
    return this.http.get<Series[]>(`${this.apiUrl}/series/`);
  }

  getSeriesById(id: string): Observable<Series> {
    return this.http.get<Series>(`${this.apiUrl}/series/${id}/`);
  }

  getSeriesChapters(seriesId: string): Observable<ChapterListItem[]> {
    return this.http.get<ChapterListItem[]>(`${this.apiUrl}/series/${seriesId}/chapters/`);
  }

  // Chapter endpoints
  getChapter(id: string): Observable<Chapter> {
    return this.http.get<Chapter>(`${this.apiUrl}/chapters/${id}/`);
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
}
