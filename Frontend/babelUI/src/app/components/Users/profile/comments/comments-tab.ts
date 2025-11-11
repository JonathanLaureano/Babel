import { Component, Input, OnInit, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { UserComment } from '../../../../models/user-data';
import { UserDataService } from '../../../../services/user-data.service';

@Component({
  selector: 'app-comments-tab',
  imports: [CommonModule],
  templateUrl: './comments-tab.html',
  styleUrl: './comments-tab.css',
  standalone: true,
})
export class CommentsTab implements OnInit, OnChanges {
  @Input() userId: string | null = null;
  
  comments: UserComment[] = [];
  loading = false;
  error: string | null = null;

  constructor(
    private userDataService: UserDataService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (this.userId) {
      this.loadComments();
    }
  }

  ngOnChanges(): void {
    if (this.userId) {
      this.loadComments();
    }
  }

  loadComments(): void {
    if (!this.userId) return;
    
    this.loading = true;
    this.error = null;

    this.userDataService.getUserComments(this.userId).subscribe({
      next: (comments) => {
        this.comments = comments;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load comments:', err);
        this.error = 'Failed to load comments';
        this.loading = false;
      }
    });
  }

  navigateToSeries(seriesId: string | undefined): void {
    if (seriesId) {
      this.router.navigate(['/series', seriesId]);
    }
  }

  navigateToComment(comment: UserComment): void {
    // If it's a chapter comment, navigate to the chapter with the comment ID as a fragment
    if (comment.series_id && comment.chapter_id) {
      this.router.navigate(
        ['/series', comment.series_id, 'chapter', comment.chapter_id],
        { fragment: comment.comment_id }
      );
    } else if (comment.series_id) {
      // If it's only a series comment, just navigate to the series
      this.router.navigate(['/series', comment.series_id]);
    }
  }
}
