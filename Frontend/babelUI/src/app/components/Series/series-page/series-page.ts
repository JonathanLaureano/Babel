import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { AuthService } from '../../../services/auth.service';
import { UserDataService } from '../../../services/user-data.service';
import { Series } from '../../../models/series';
import { ChapterListItem } from '../../../models/chapter';
import { Bookmark } from '../../../models/user-data';
import { StarRatingComponent } from '../star-rating/star-rating';
import { RatingSubmitComponent } from '../rating-submit/rating-submit';
import { CommentsComponent } from '../../Users/comments/comments';

@Component({
  selector: 'app-series-page',
  imports: [CommonModule, RouterModule, StarRatingComponent, RatingSubmitComponent, CommentsComponent],
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
  currentBookmark: Bookmark | null = null;
  bookmarkLoading = false;

  constructor(
    private route: ActivatedRoute,
    private libraryService: LibraryService,
    private authService: AuthService,
    private userDataService: UserDataService
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
        
        // Check bookmark status if logged in
        if (this.isLoggedIn) {
          this.checkBookmarkStatus(seriesData.series_id);
        }
        
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
        this.error = 'Failed to load series.';
        this.loading = false;
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

  checkBookmarkStatus(seriesId: string): void {
    const user = this.authService.getCurrentUser();
    if (!user) return;

    this.userDataService.checkBookmarkExists(user.user_id, seriesId).subscribe({
      next: (bookmark) => {
        this.currentBookmark = bookmark;
      },
      error: (err) => {
        console.error('Error checking bookmark status:', err);
      }
    });
  }

  toggleBookmark(): void {
    if (!this.series || this.bookmarkLoading) return;

    const user = this.authService.getCurrentUser();
    if (!user) {
      alert('Please log in to bookmark this series.');
      return;
    }

    this.bookmarkLoading = true;

    if (this.currentBookmark) {
      // Remove bookmark
      this.userDataService.deleteBookmark(this.currentBookmark.bookmark_id).subscribe({
        next: () => {
          this.currentBookmark = null;
          this.bookmarkLoading = false;
        },
        error: (err) => {
          console.error('Error removing bookmark:', err);
          alert('Failed to remove bookmark. Please try again.');
          this.bookmarkLoading = false;
        }
      });
    } else {
      // Add bookmark
      this.userDataService.createBookmark({ series: this.series.series_id }).subscribe({
        next: (bookmark) => {
          this.currentBookmark = bookmark;
          this.bookmarkLoading = false;
        },
        error: (err) => {
          console.error('Error adding bookmark:', err);
          alert('Failed to add bookmark. Please try again.');
          this.bookmarkLoading = false;
        }
      });
    }
  }
}
