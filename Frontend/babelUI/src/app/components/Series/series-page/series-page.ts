import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { AuthService } from '../../../services/auth.service';
import { Series } from '../../../models/series';
import { ChapterListItem } from '../../../models/chapter';
import { StarRatingComponent } from '../star-rating/star-rating';
import { RatingSubmitComponent } from '../rating-submit/rating-submit';

@Component({
  selector: 'app-series-page',
  imports: [CommonModule, RouterModule, StarRatingComponent, RatingSubmitComponent],
  templateUrl: './series-page.html',
  styleUrl: './series-page.css',
  standalone: true,
})
export class SeriesPage implements OnInit {
  series: Series | null = null;
  chapters: ChapterListItem[] = [];
  loading = true;
  error: string | null = null;
  isLoggedIn = false;

  constructor(
    private route: ActivatedRoute,
    private libraryService: LibraryService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.isLoggedIn = this.authService.isLoggedIn();
    
    this.route.params.subscribe(params => {
      const id = params['id'];
      if (id) {
        this.loadSeriesData(id);
      }
    });
  }

  loadSeriesData(id: string): void {
    this.loading = true;
    this.error = null;
    this.chapters = []; // Reset chapters array

    console.log('Loading series with ID:', id); // Debug log

    // Get the series by ID
    this.libraryService.getSeriesById(id).subscribe({
      next: (seriesData: Series) => {
        console.log('Series data received:', seriesData); // Debug log
        this.series = seriesData;
        
        // Track the view
        this.trackView(seriesData.series_id);
        
        // Then fetch chapters for this series
        this.libraryService.getSeriesChapters(seriesData.series_id).subscribe({
          next: (chaptersData: ChapterListItem[]) => {
            console.log('Chapters data received:', chaptersData); // Debug log
            this.chapters = chaptersData.sort((a, b) => a.chapter_number - b.chapter_number);
            this.loading = false;
          },
          error: (err: any) => {
            console.error('Error loading chapters:', err);
            this.error = 'Failed to load chapters.';
            this.loading = false;
          }
        });
      },
      error: (err: any) => {
        console.error('Error loading series:', err);
          }
    });
  }

  trackView(seriesId: string): void {
    this.libraryService.trackSeriesView(seriesId).subscribe({
      next: (response) => {
        console.log('View tracked:', response);
        // Optionally update the view count in the UI
        if (this.series && response.view_count !== undefined) {
          this.series.total_view_count = response.view_count;
        }
      },
      error: (err) => {
        console.error('Error tracking view:', err);
        // Don't show error to user, view tracking is not critical
      }
    });
  }

  onRatingSubmitted(): void {
    // Reload series data to get updated average rating
    if (this.series) {
      this.libraryService.getSeriesById(this.series.series_id).subscribe({
        next: (seriesData: Series) => {
          this.series = seriesData;
        },
        error: (err) => {
          console.error('Error reloading series:', err);
        }
      });
    }
  }
}
