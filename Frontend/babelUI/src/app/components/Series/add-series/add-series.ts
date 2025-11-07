import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Genre } from '../../../models/genre';

@Component({
  selector: 'app-add-series',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './add-series.html',
  styleUrls: ['./add-series.css']
})
export class AddSeries implements OnInit {
  series = {
    title: '',
    description: '',
    cover_image_url: '',
    status: 'Ongoing',
    genre_ids: [] as string[]
  };
  genres: Genre[] = [];
  error: string | null = null;
  loading = false;

  constructor(private libraryService: LibraryService, private router: Router) {}

  ngOnInit(): void {
    this.libraryService.getGenres().subscribe({
      next: (genres) => {
        this.genres = genres;
      },
      error: (err) => {
        this.error = 'Failed to load genres. Please try again later.';
        console.error(err);
      }
    });
  }

  onSubmit(): void {
    this.loading = true;
    this.error = null;
    this.libraryService.createSeries(this.series).subscribe({
      next: () => {
        this.router.navigate(['/staff']);
      },
      error: (err) => {
        this.error = 'Failed to create series. Please check the form and try again.';
        this.loading = false;
        console.error(err);
      }
    });
  }
}
