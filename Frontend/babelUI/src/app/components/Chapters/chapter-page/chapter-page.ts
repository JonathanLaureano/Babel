import { Component, OnInit, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Chapter, ChapterListItem } from '../../../models/chapter';
import { forkJoin } from 'rxjs';
import { Series } from '../../../models/series';
import { CommentsComponent } from '../../Users/comments/comments';
import { AuthService } from '../../../services/auth.service';
import { UserDataService } from '../../../services/user-data.service';

@Component({
  selector: 'app-chapter-page',
  imports: [CommonModule, RouterModule, CommentsComponent],
  templateUrl: './chapter-page.html',
  styleUrl: './chapter-page.css',
  standalone: true,
})
export class ChapterPage implements OnInit, AfterViewChecked {
  chapter: Chapter | null = null;
  prevChapter: ChapterListItem | null = null;
  nextChapter: ChapterListItem | null = null;
  loading = true;
  error: string | null = null;
  private pendingCommentId: string | null = null;
  private hasScrolledToComment = false;
  private scrollAttempts = 0;
  private readonly MAX_SCROLL_ATTEMPTS = 50; // Limit retries to avoid infinite loops

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private libraryService: LibraryService,
    private authService: AuthService,
    private userDataService: UserDataService
  ) { }

  ngOnInit(): void {
    // Subscribe to route parameter changes instead of using snapshot
    this.route.paramMap.subscribe(params => {
      const chapterId = params.get('chapterId');
      const seriesId = params.get('id');
      if (seriesId && chapterId) {
        this.loadChapterData(seriesId, chapterId);
      } else {
        this.error = 'Missing series or chapter ID.';
        this.loading = false;
      }
    });

    // Handle fragment to scroll to specific comment
    this.route.fragment.subscribe(fragment => {
      if (fragment) {
        this.pendingCommentId = fragment;
        this.hasScrolledToComment = false;
        this.scrollAttempts = 0;
      }
    });
  }

  ngAfterViewChecked(): void {
    // Attempt to scroll to comment after view has been checked and rendered
    // Only attempt if we have a pending comment, haven't scrolled yet, and haven't exceeded max attempts
    if (this.pendingCommentId && !this.hasScrolledToComment && !this.loading) {
      if (this.scrollAttempts < this.MAX_SCROLL_ATTEMPTS) {
        this.scrollAttempts++;
        this.scrollToComment(this.pendingCommentId);
      } else {
        // Give up after max attempts - comment may not exist or comments haven't loaded
        console.warn(`Failed to scroll to comment ${this.pendingCommentId} after ${this.MAX_SCROLL_ATTEMPTS} attempts`);
        this.pendingCommentId = null;
        this.scrollAttempts = 0;
      }
    }
  }

  loadChapterData(id: string, chapterId: string): void {
    this.loading = true;
    this.error = null;

    // First get the series by slug to get the series_id
    this.libraryService.getSeriesById(id).subscribe({
      next: (series: Series) => {
        // Now load chapter and all chapters using series_id
        forkJoin({
          chapter: this.libraryService.getChapter(chapterId),
          allChapters: this.libraryService.getSeriesChapters(series.series_id)
        }).subscribe({
          next: ({ chapter, allChapters }) => {
            this.chapter = chapter;
            
            // Track the chapter view
            this.trackView(chapterId);
            
            // Track reading history for logged-in users
            this.trackReadingHistory(series.series_id, chapterId);
            
            const sortedChapters = allChapters.sort((a: ChapterListItem, b: ChapterListItem) => a.chapter_number - b.chapter_number);
            const currentIndex = sortedChapters.findIndex(c => c.chapter_id === chapter.chapter_id);

            this.prevChapter = currentIndex > 0 ? sortedChapters[currentIndex - 1] : null;
            this.nextChapter = currentIndex < sortedChapters.length - 1 ? sortedChapters[currentIndex + 1] : null;
            
            this.loading = false;
          },
          error: (err: any) => {
            console.error('Error loading chapter details:', err);
            this.error = 'Failed to load chapter details.';
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

  navigateToChapter(seriesId: string, chapterId: string): void {
    this.router.navigate(['/series', seriesId, 'chapter', chapterId]);
  }

  trackView(chapterId: string): void {
    this.libraryService.trackChapterView(chapterId).subscribe({
      next: (response) => {
        // Update the view count in the UI
        if (this.chapter && response.view_count !== undefined) {
          this.chapter.view_count = response.view_count;
        }
      },
      error: () => {
        // Don't show error to user, view tracking is not critical
      }
    });
  }

  trackReadingHistory(seriesId: string, chapterId: string): void {
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser) {
      // User not logged in, skip tracking
      return;
    }

    this.userDataService.updateReadingHistory({
      series: seriesId,
      chapter: chapterId
    }).subscribe({
      next: () => {
        // Reading history updated successfully
      },
      error: () => {
        // Don't show error to user, history tracking is not critical
      }
    });
  }

  scrollToComment(commentId: string): void {
    const element = document.getElementById('comment-' + commentId);
    if (element) {
      this.hasScrolledToComment = true;
      this.pendingCommentId = null;
      this.scrollAttempts = 0;
      
      // Use requestAnimationFrame to ensure DOM is fully rendered
      requestAnimationFrame(() => {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Add a highlight effect
        element.classList.add('highlight');
        setTimeout(() => {
          element.classList.remove('highlight');
        }, 2000);
      });
    }
  }
}
