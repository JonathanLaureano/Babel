import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LibraryService } from '../../services/library.service';
import { Chapter } from '../../models/chapter';

@Component({
  selector: 'app-chapter-reader',
  imports: [CommonModule, RouterModule],
  templateUrl: './chapter-reader.component.html',
  styleUrl: './chapter-reader.component.css'
})
export class ChapterReaderComponent implements OnInit {
  chapter: Chapter | null = null;
  loading = true;
  error: string | null = null;
  hasNext = false;
  hasPrevious = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private libraryService: LibraryService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadChapter(id);
    }
  }

  loadChapter(id: string): void {
    this.loading = true;
    this.error = null;
    
    this.libraryService.getChapter(id).subscribe({
      next: (data) => {
        this.chapter = data;
        this.loading = false;
        this.checkNavigation(id);
      },
      error: (err) => {
        this.error = 'Failed to load chapter. Please try again later.';
        this.loading = false;
        console.error('Error loading chapter:', err);
      }
    });
  }

  checkNavigation(id: string): void {
    // Check for next chapter
    this.libraryService.getNextChapter(id).subscribe({
      next: () => this.hasNext = true,
      error: () => this.hasNext = false
    });

    // Check for previous chapter
    this.libraryService.getPreviousChapter(id).subscribe({
      next: () => this.hasPrevious = true,
      error: () => this.hasPrevious = false
    });
  }

  navigateToNext(): void {
    if (this.chapter && this.hasNext) {
      this.libraryService.getNextChapter(this.chapter.chapter_id).subscribe({
        next: (nextChapter) => {
          this.router.navigate(['/chapter', nextChapter.chapter_id]);
          this.loadChapter(nextChapter.chapter_id);
        }
      });
    }
  }

  navigateToPrevious(): void {
    if (this.chapter && this.hasPrevious) {
      this.libraryService.getPreviousChapter(this.chapter.chapter_id).subscribe({
        next: (prevChapter) => {
          this.router.navigate(['/chapter', prevChapter.chapter_id]);
          this.loadChapter(prevChapter.chapter_id);
        }
      });
    }
  }
}
