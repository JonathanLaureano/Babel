import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { LibraryService } from '../../services/library.service';
import { Series } from '../../models/series';
import { ChapterListItem } from '../../models/chapter';

@Component({
  selector: 'app-series-detail',
  imports: [CommonModule, RouterModule],
  templateUrl: './series-detail.component.html',
  styleUrl: './series-detail.component.css'
})
export class SeriesDetailComponent implements OnInit {
  series: Series | null = null;
  chapters: ChapterListItem[] = [];
  loading = true;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private libraryService: LibraryService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadSeriesDetails(id);
    }
  }

  loadSeriesDetails(id: string): void {
    this.libraryService.getSeriesById(id).subscribe({
      next: (data) => {
        this.series = data;
        this.loadChapters(id);
      },
      error: (err) => {
        this.error = 'Failed to load series details. Please try again later.';
        this.loading = false;
        console.error('Error loading series:', err);
      }
    });
  }

  loadChapters(seriesId: string): void {
    this.libraryService.getSeriesChapters(seriesId).subscribe({
      next: (data) => {
        this.chapters = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load chapters. Please try again later.';
        this.loading = false;
        console.error('Error loading chapters:', err);
      }
    });
  }
}
