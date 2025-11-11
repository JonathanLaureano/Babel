export interface TranslationJob {
  job_id: string;
  novel_url: string;
  status: 'pending' | 'scraping' | 'translating' | 'completed' | 'failed';
  korean_title?: string;
  korean_author?: string;
  korean_genre?: string;
  korean_description?: string;
  cover_image_url?: string;
  english_title?: string;
  english_author?: string;
  english_genre?: string;
  english_description?: string;
  prompt_dictionary?: Record<string, string>;
  chapters_requested: number;
  chapters_completed: number;
  chapters_failed: number;
  progress_percentage: number;
  current_operation?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  imported_series?: string;
  cached_chapters?: TranslatedChapterCache[];
}

export interface TranslatedChapterCache {
  cache_id: string;
  chapter_number: number;
  chapter_url: string;
  korean_title: string;
  korean_content: string;
  english_title?: string;
  english_content_raw?: string;
  english_content_final?: string;
  word_count?: number;
  status: 'pending' | 'scraped' | 'translated' | 'polished' | 'failed';
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTranslationJobRequest {
  novel_url: string;
  chapters_requested?: number;
  translate_all?: boolean;
  prompt_dictionary?: Record<string, string>;
}

export interface TranslationJobPreview {
  job_id: string;
  status: string;
  english_title: string;
  english_author: string;
  english_genre: string;
  english_description: string;
  chapters_requested: number;
  chapters_completed: number;
  chapters: ChapterPreview[];
}

export interface ChapterPreview {
  cache_id: string;
  chapter_number: number;
  english_title: string;
  word_count: number;
  status: string;
}

export interface ImportTranslationRequest {
  cover_image_url?: string;
  status: 'Ongoing' | 'Completed' | 'Hiatus';
  selected_chapters?: number[];
}

export interface ImportTranslationResponse {
  message: string;
  series_id: string;
  series_title: string;
  chapters_imported: number;
}
