import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LibraryService } from '../../services/library.service';
import { Series } from '../../models/series';

@Component({
  selector: 'app-series-list',
  imports: [CommonModule, RouterModule],
  templateUrl: './series-list.component.html',
  styleUrl: './series-list.component.css'
})
export class SeriesListComponent implements OnInit {
  series: Series[] = [];
  loading = true;
  error: string | null = null;

  constructor(private libraryService: LibraryService) {}

  ngOnInit(): void {
    this.loadSeries();
  }

  loadSeries(): void {
    this.libraryService.getSeries().subscribe({
      next: (data) => {
        this.series = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load series. Please try again later.';
        this.loading = false;
        console.error('Error loading series:', err);
      }
    });
  }
}
