import { Series } from './series';
import { Comment } from './comment';

export interface Bookmark {
  bookmark_id: string;
  user: string;
  series: string;
  series_details?: Series;
  created_at: string;
}

export interface ReadingHistory {
  history_id: string;
  user: string;
  series: string;
  chapter: string;
  series_title?: string;
  chapter_number?: number;
  chapter_title?: string;
  last_read_at: string;
}

export interface UserComment extends Comment {
  series_id?: string;
  series_title?: string;
  chapter_id?: string;
  chapter_title?: string;
}

export interface CreateBookmarkRequest {
  series: string;
}

export interface UpdateReadingHistoryRequest {
  series: string;
  chapter: string;
}
