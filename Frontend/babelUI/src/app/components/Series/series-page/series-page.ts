import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Series } from '../../../models/series';
import { ChapterListItem } from '../../../models/chapter';

@Component({
  selector: 'app-series-page',
  imports: [CommonModule, RouterModule],
  templateUrl: './series-page.html',
  styleUrl: './series-page.css',
  standalone: true,
})
export class SeriesPage implements OnInit {
  series: Series | null = null;
  chapters: ChapterListItem[] = []; // Initialize as empty array instead of undefined
  loading = true;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private libraryService: LibraryService
  ) {}

  ngOnInit(): void {
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
        this.error = 'Failed to load series details.';
        this.loading = false;
      }
    });
  }
}