import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Series } from '../../../models/series';
import { ChapterListItem } from '../../../models/chapter';
import { forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

interface SeriesWithRecentChapters extends Series {
  recent_chapters?: ChapterListItem[];
}

@Component({
  selector: 'app-homepage',
  imports: [CommonModule, RouterModule],
  templateUrl: './homepage.html',
  styleUrl: './homepage.css',
  standalone: true,
})
export class Homepage implements OnInit {
  series: SeriesWithRecentChapters[] = [];
  loading = true;
  error: string | null = null;

  constructor(private libraryService: LibraryService) {}

  ngOnInit(): void {
    this.loadSeries();
  }

  loadSeries(): void {
    this.loading = true;
    this.error = null;

    console.log('Loading series...');

    this.libraryService.getSeries().subscribe({
      next: (data: Series[]) => {
        console.log('Series data received:', data);
        
        // Fetch recent chapters for each series
        const seriesWithChapters$ = data.map(s => 
          this.libraryService.getSeriesChapters(s.series_id).pipe(
            map(chapters => ({
              ...s,
              recent_chapters: chapters.slice(-3).reverse() // Get last 3 chapters, most recent first
            })),
            catchError(() => of({ ...s, recent_chapters: [] }))
          )
        );

        if (seriesWithChapters$.length > 0) {
          forkJoin(seriesWithChapters$).subscribe({
            next: (seriesData) => {
              this.series = seriesData;
              this.loading = false;
            },
            error: (err: any) => {
              console.error('Error loading chapter data:', err);
              this.series = data.map(s => ({ ...s, recent_chapters: [] }));
              this.loading = false;
            }
          });
        } else {
          this.series = [];
          this.loading = false;
        }
      },
      error: (err: any) => {
        console.error('Error loading series:', err);
        this.error = 'Failed to load series. Please try again later.';
        this.loading = false;
      }
    });
  }
}
