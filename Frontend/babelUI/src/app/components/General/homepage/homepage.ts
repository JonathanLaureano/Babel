import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Series } from '../../../models/series';

@Component({
  selector: 'app-homepage',
  imports: [CommonModule, RouterModule],
  templateUrl: './homepage.html',
  styleUrl: './homepage.css',
  standalone: true,
})
export class Homepage implements OnInit {
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

    console.log('Loading series...');

    this.libraryService.getSeries().subscribe({
      next: (data: Series[]) => {
        console.log('Series data received:', data);
        this.series = data;
        this.loading = false;
      },
      error: (err: any) => {
        console.error('Error loading series:', err);
        this.error = 'Failed to load series. Please try again later.';
        this.loading = false;
      }
    });
  }
}
