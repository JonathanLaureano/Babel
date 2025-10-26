export interface Chapter {
  chapter_id: string;
  series: string;
  series_title: string;
  chapter_number: number;
  title: string;
  content: string;
  word_count?: number;
  publication_date?: string;
  created_at: string;
  updated_at: string;
}

export interface ChapterListItem {
  chapter_id: string;
  series: string;
  series_title: string;
  chapter_number: number;
  title: string;
  word_count?: number;
  publication_date?: string;
  created_at: string;
  updated_at: string;
}
