import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LibraryService } from '../../services/library.service';
import { Series } from '../../models/series';

@Component({
  selector: 'app-all-series',
  imports: [CommonModule, RouterModule],
  templateUrl: './all-series.html',
  styleUrl: './all-series.css'
})
export class AllSeries implements OnInit {
  series: Series[] = [];
  loading = true;
  error: string | null = null;

  constructor(private libraryService: LibraryService) {}

  ngOnInit(): void {
    this.loadSeries();
  }

  loadSeries(): void {
    this.loading = true;
    this.error = null;

    this.libraryService.getSeries().subscribe({
      next: (data) => {
        this.series = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading series:', err);
        this.error = 'Failed to load series.';
        this.loading = false;
      }
    });
  }
}
