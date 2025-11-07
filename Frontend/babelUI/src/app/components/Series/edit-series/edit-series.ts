import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Genre } from '../../../models/genre';
import { Series } from '../../../models/series';

@Component({
  selector: 'app-edit-series',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './edit-series.html',
  styleUrls: ['./edit-series.css']
})
export class EditSeries implements OnInit {
  series: Series | null = null;
  seriesUpdateData = {
    title: '',
    description: '',
    cover_image_url: '',
    status: 'Ongoing',
    genre_ids: [] as string[]
  };
  genres: Genre[] = [];
  error: string | null = null;
  loading = true;
  seriesId: string | null = null;

  constructor(
    private libraryService: LibraryService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.seriesId = this.route.snapshot.paramMap.get('id');
    if (!this.seriesId) {
      this.error = "Series ID not found.";
      this.loading = false;
      return;
    }

    this.libraryService.getGenres().subscribe({
      next: (genres) => {
        this.genres = genres;
      },
      error: (err) => {
        this.error = "Failed to load genres.";
        this.loading = false;
        console.error(err);
      }
    });

    this.libraryService.getSeriesById(this.seriesId).subscribe({
      next: (series) => {
        this.series = series;
        this.seriesUpdateData = {
          title: series.title,
          description: series.description || '',
          cover_image_url: series.cover_image_url || '',
          status: series.status,
          genre_ids: series.genres.map(g => g.genre_id)
        };
        this.loading = false;
      },
      error: (err) => {
        this.error = "Failed to load series data.";
        this.loading = false;
        console.error(err);
      }
    });
  }

  onSubmit(): void {
    if (!this.seriesId) return;
    this.loading = true;
    this.error = null;
    this.libraryService.updateSeries(this.seriesId, this.seriesUpdateData).subscribe({
      next: () => {
        this.router.navigate(['/staff']);
      },
      error: (err) => {
        this.error = 'Failed to update series.';
        this.loading = false;
        console.error(err);
      }
    });
  }
}
