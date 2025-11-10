import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  TranslationJob,
  TranslatedChapterCache,
  CreateTranslationJobRequest,
  TranslationJobPreview,
  ImportTranslationRequest,
  ImportTranslationResponse
} from '../models/translator';

@Injectable({
  providedIn: 'root'
})
export class TranslatorService {
  private apiUrl = 'http://localhost:8000/api/translator';

  constructor(private http: HttpClient) { }

  // Get all translation jobs
  getJobs(): Observable<TranslationJob[]> {
    return this.http.get<TranslationJob[]>(`${this.apiUrl}/jobs/`);
  }

  // Get single job details with all chapters
  getJob(jobId: string): Observable<TranslationJob> {
    return this.http.get<TranslationJob>(`${this.apiUrl}/jobs/${jobId}/`);
  }

  // Create new translation job
  createJob(request: CreateTranslationJobRequest): Observable<TranslationJob> {
    return this.http.post<TranslationJob>(`${this.apiUrl}/jobs/`, request);
  }

  // Get job preview
  getJobPreview(jobId: string): Observable<TranslationJobPreview> {
    return this.http.get<TranslationJobPreview>(`${this.apiUrl}/jobs/${jobId}/preview/`);
  }

  // Get all chapters for a job
  getJobChapters(jobId: string): Observable<TranslatedChapterCache[]> {
    return this.http.get<TranslatedChapterCache[]>(`${this.apiUrl}/jobs/${jobId}/chapters/`);
  }

  // Import job to library
  importToLibrary(jobId: string, request: ImportTranslationRequest): Observable<ImportTranslationResponse> {
    return this.http.post<ImportTranslationResponse>(
      `${this.apiUrl}/jobs/${jobId}/import_to_library/`,
      request
    );
  }

  // Delete job
  deleteJob(jobId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/jobs/${jobId}/`);
  }
}
