import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LibraryService } from '../../../services/library.service';

@Component({
  selector: 'app-rating-submit',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rating-submit.html',
  styleUrl: './rating-submit.css'
})
export class RatingSubmitComponent {
  @Input() seriesId!: string;
  @Output() ratingSubmitted = new EventEmitter<void>();

  selectedRating: number = 0;
  hoverRating: number = 0;
  hasRated: boolean = false;
  submitting: boolean = false;
  error: string | null = null;

  constructor(private libraryService: LibraryService) {}

  selectRating(rating: number): void {
    this.selectedRating = rating;
    this.error = null;
  }

  submitRating(): void {
    if (!this.selectedRating) {
      this.error = 'Please select a rating';
      return;
    }

    this.submitting = true;
    this.error = null;

    this.libraryService.rateSeriesRating(this.seriesId, this.selectedRating).subscribe({
      next: () => {
        this.hasRated = true;
        this.submitting = false;
        this.ratingSubmitted.emit();
      },
      error: (err) => {
        this.submitting = false;
        if (err.status === 400 && err.error?.error?.includes('already rated')) {
          this.error = 'You have already rated this series';
          this.hasRated = true;
        } else if (err.status === 401) {
          this.error = 'Please log in to rate this series';
        } else {
          this.error = 'Failed to submit rating. Please try again.';
        }
      }
    });
  }
}
