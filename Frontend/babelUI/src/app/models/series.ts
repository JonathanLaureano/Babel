import { Genre } from './genre';

export interface Series {
  series_id: string;
  title: string;
  author?: string;
  description?: string;
  cover_image_url?: string;
  status: 'Ongoing' | 'Completed' | 'Hiatus';
  genres: Genre[];
  chapters_count: number;
  average_rating: number;
  total_view_count: number;
  created_at: string;
  updated_at: string;
}
