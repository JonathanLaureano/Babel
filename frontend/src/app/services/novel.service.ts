import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Novel, Chapter } from '../models/novel';

@Injectable({
  providedIn: 'root'
})
export class NovelService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  getNovels(): Observable<Novel[]> {
    return this.http.get<Novel[]>(`${this.apiUrl}/novels/`);
  }

  getNovel(id: number): Observable<Novel> {
    return this.http.get<Novel>(`${this.apiUrl}/novels/${id}/`);
  }

  createNovel(novel: Partial<Novel>): Observable<Novel> {
    return this.http.post<Novel>(`${this.apiUrl}/novels/`, novel);
  }

  updateNovel(id: number, novel: Partial<Novel>): Observable<Novel> {
    return this.http.put<Novel>(`${this.apiUrl}/novels/${id}/`, novel);
  }

  deleteNovel(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/novels/${id}/`);
  }

  getChapters(novelId: number): Observable<Chapter[]> {
    return this.http.get<Chapter[]>(`${this.apiUrl}/chapters/?novel=${novelId}`);
  }

  getChapter(id: number): Observable<Chapter> {
    return this.http.get<Chapter>(`${this.apiUrl}/chapters/${id}/`);
  }

  createChapter(chapter: Partial<Chapter>): Observable<Chapter> {
    return this.http.post<Chapter>(`${this.apiUrl}/chapters/`, chapter);
  }

  updateChapter(id: number, chapter: Partial<Chapter>): Observable<Chapter> {
    return this.http.put<Chapter>(`${this.apiUrl}/chapters/${id}/`, chapter);
  }

  deleteChapter(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/chapters/${id}/`);
  }
}

