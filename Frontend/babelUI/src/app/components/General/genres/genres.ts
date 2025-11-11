import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Series } from '../../../models/series';
import { Genre } from '../../../models/genre';

@Component({
  selector: 'app-genres',
  imports: [CommonModule, RouterModule],
  templateUrl: './genres.html',
  styleUrl: './genres.css',
  standalone: true,
})
export class Genres implements OnInit {
  series: Series[] = [];
  allGenres: Genre[] = [];
  selectedGenres: string[] = [];
  loading = true;
  error: string | null = null;

  constructor(
    private libraryService: LibraryService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Load all available genres
    this.libraryService.getGenres().subscribe({
      next: (genres: Genre[]) => {
        this.allGenres = genres;
      },
      error: (err: any) => {
        console.error('Error loading genres:', err);
      }
    });

    // Watch for query param changes
    this.route.queryParams.subscribe(params => {
      const genreParam = params['genre'];
      if (genreParam) {
        this.selectedGenres = Array.isArray(genreParam) ? genreParam : [genreParam];
      } else {
        this.selectedGenres = [];
      }
      this.loadSeriesByGenres();
    });
  }

  loadSeriesByGenres(): void {
    this.loading = true;
    this.error = null;

    // Use consolidated getSeries method with optional genre filtering
    this.libraryService.getSeries(undefined, this.selectedGenres.length > 0 ? this.selectedGenres : undefined).subscribe({
      next: (data: Series[]) => {
        this.series = data;
        this.loading = false;
      },
      error: (err: any) => {
        console.error('Error loading series:', err);
        this.error = 'Failed to load series.';
        this.loading = false;
      }
    });
  }

  isGenreSelected(genreId: string): boolean {
    return this.selectedGenres.includes(genreId);
  }

  toggleGenre(genreId: string): void {
    if (this.isGenreSelected(genreId)) {
      this.selectedGenres = this.selectedGenres.filter(id => id !== genreId);
    } else {
      this.selectedGenres = [...this.selectedGenres, genreId];
    }
    
    // Update URL with query params
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { genre: this.selectedGenres.length > 0 ? this.selectedGenres : null },
      queryParamsHandling: 'merge'
    });
  }

  clearGenres(): void {
    this.selectedGenres = [];
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { genre: null },
      queryParamsHandling: 'merge'
    });
  }

  getGenreName(genreId: string): string {
    const genre = this.allGenres.find(g => g.genre_id === genreId);
    return genre ? genre.name : '';
  }
}
