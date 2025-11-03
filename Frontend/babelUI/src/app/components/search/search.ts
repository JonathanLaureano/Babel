import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, takeUntil } from 'rxjs';
import { LibraryService } from '../../services/library.service';
import { Series } from '../../models/series';

@Component({
  selector: 'app-search',
  imports: [CommonModule, FormsModule],
  templateUrl: './search.html',
  styleUrl: './search.css'
})
export class SearchComponent implements OnDestroy {
  query = '';
  results: Series[] = [];
  loading = false;
  private destroy$ = new Subject<void>();
  private searchSubject = new Subject<string>();

  constructor(
    private libraryService: LibraryService,
    private router: Router
  ) {
    this.searchSubject
      .pipe(debounceTime(300), takeUntil(this.destroy$))
      .subscribe((query) => this.performSearch(query));
  }

  onInputChange(): void {
    this.searchSubject.next(this.query);
  }

  performSearch(searchQuery: string): void {
    if (!searchQuery.trim()) {
      this.results = [];
      return;
    }

    this.loading = true;
    this.libraryService.getSeries(searchQuery).subscribe({
      next: (series) => {
        this.results = series;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to fetch series for search:', err);
        this.results = [];
        this.loading = false;
      }
    });
  }

  selectSeries(slug: string): void {
    this.router.navigate(['/series', slug]);
    this.query = '';
    this.results = [];
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
