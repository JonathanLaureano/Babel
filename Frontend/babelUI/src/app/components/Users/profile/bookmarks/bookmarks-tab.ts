import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Bookmark, ReadingHistory } from '../../../../models/user-data';
import { UserDataService } from '../../../../services/user-data.service';

interface BookmarkWithHistory extends Bookmark {
  lastReadChapter?: ReadingHistory;
}

@Component({
  selector: 'app-bookmarks-tab',
  imports: [CommonModule],
  templateUrl: './bookmarks-tab.html',
  styleUrl: './bookmarks-tab.css',
  standalone: true,
})
export class BookmarksTab implements OnInit {
  @Input() userId: string | null = null;
  
  bookmarks: BookmarkWithHistory[] = [];
  loading = false;
  error: string | null = null;

  constructor(
    private userDataService: UserDataService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (this.userId) {
      this.loadBookmarks();
    }
  }

  ngOnChanges(): void {
    if (this.userId) {
      this.loadBookmarks();
    }
  }

  loadBookmarks(): void {
    if (!this.userId) return;
    
    this.loading = true;
    this.error = null;

    this.userDataService.getUserBookmarks(this.userId).subscribe({
      next: (bookmarks) => {
        this.bookmarks = bookmarks;
        // Load reading history for each bookmarked series
        this.loadReadingHistoryForBookmarks();
      },
      error: (err) => {
        console.error('Failed to load bookmarks:', err);
        this.error = 'Failed to load bookmarks';
        this.loading = false;
      }
    });
  }

  loadReadingHistoryForBookmarks(): void {
    if (!this.userId) {
      this.loading = false;
      return;
    }

    if (this.bookmarks.length === 0) {
      this.loading = false;
      return;
    }

    let pendingRequests = this.bookmarks.length;

    this.bookmarks.forEach((bookmark, index) => {
      this.userDataService.getSeriesReadingHistory(this.userId!, bookmark.series).subscribe({
        next: (history) => {
          if (history) {
            this.bookmarks[index].lastReadChapter = history;
          }
          pendingRequests--;
          if (pendingRequests === 0) {
            this.loading = false;
          }
        },
        error: (err) => {
          console.error('Failed to load reading history for series:', bookmark.series, err);
          pendingRequests--;
          if (pendingRequests === 0) {
            this.loading = false;
          }
        }
      });
    });
  }

  navigateToSeries(seriesId: string): void {
    this.router.navigate(['/series', seriesId]);
  }

  resumeReading(bookmark: BookmarkWithHistory): void {
    if (bookmark.lastReadChapter) {
      this.router.navigate(['/series', bookmark.series, 'chapter', bookmark.lastReadChapter.chapter]);
    } else {
      // If no reading history, navigate to the series page
      this.navigateToSeries(bookmark.series);
    }
  }

  removeBookmark(bookmarkId: string): void {
    if (!confirm('Remove this series from your bookmarks?')) {
      return;
    }

    this.userDataService.deleteBookmark(bookmarkId).subscribe({
      next: () => {
        this.bookmarks = this.bookmarks.filter(b => b.bookmark_id !== bookmarkId);
      },
      error: (err) => {
        console.error('Failed to remove bookmark:', err);
        alert('Failed to remove bookmark. Please try again.');
      }
    });
  }
}
