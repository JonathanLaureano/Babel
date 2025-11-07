import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-star-rating',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './star-rating.html',
  styleUrl: './star-rating.css'
})
export class StarRatingComponent {
  @Input() rating: number = 0;
  @Input() showValue: boolean = true;
  stars: string[] = [];

  ngOnChanges(): void {
    this.updateStars();
  }

  ngOnInit(): void {
    this.updateStars();
  }

  private updateStars(): void {
    this.stars = [];
    const fullStars = Math.floor(this.rating);
    const hasHalfStar = this.rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    for (let i = 0; i < fullStars; i++) {
      this.stars.push('full');
    }

    if (hasHalfStar) {
      this.stars.push('half');
    }

    for (let i = 0; i < emptyStars; i++) {
      this.stars.push('empty');
    }
  }

  getStarIcon(type: string): string {
    switch (type) {
      case 'full':
        return '★';
      case 'half':
        return '★'; // Using full star with different styling
      case 'empty':
        return '☆';
      default:
        return '';
    }
  }
}
