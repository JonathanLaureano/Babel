import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Chapter, ChapterListItem } from '../../../models/chapter';
import { forkJoin } from 'rxjs';
import { Series } from '../../../models/series';

@Component({
  selector: 'app-chapter-page',
  imports: [CommonModule, RouterModule],
  templateUrl: './chapter-page.html',
  styleUrl: './chapter-page.css',
  standalone: true,
})
export class ChapterPage implements OnInit {
  chapter: Chapter | null = null;
  prevChapter: ChapterListItem | null = null;
  nextChapter: ChapterListItem | null = null;
  loading = true;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private libraryService: LibraryService
  ) { }

  ngOnInit(): void {
    const chapterId = this.route.snapshot.paramMap.get('chapterId');
    const seriesId = this.route.snapshot.paramMap.get('id');
    if (seriesId && chapterId) {
      this.loadChapterData(seriesId, chapterId);
    } else {
      this.error = 'Missing series or chapter ID.';
      this.loading = false;
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
}
