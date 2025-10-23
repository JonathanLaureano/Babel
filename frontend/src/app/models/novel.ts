export interface Novel {
  id: number;
  title: string;
  original_language: string;
  target_language: string;
  author: string;
  description: string;
  chapter_count?: number;
  chapters?: Chapter[];
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: number;
  chapter_number: number;
  title: string;
  original_content: string;
  translated_content: string;
  created_at: string;
  updated_at: string;
}

