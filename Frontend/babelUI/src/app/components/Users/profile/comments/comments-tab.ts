import { Component, Input, OnInit } from '@angular/core';
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
export class CommentsTab implements OnInit {
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
    console.log('Click detected! Navigating to comment:', comment);
    console.log('Comment has series_id:', comment.series_id);
    console.log('Comment has chapter_id:', comment.chapter_id);
    console.log('Comment has comment_id:', comment.comment_id);
    
    // If it's a chapter comment, navigate to the chapter with the comment ID as a fragment
    if (comment.series_id && comment.chapter_id) {
      const path = ['/series', comment.series_id, 'chapter', comment.chapter_id];
      console.log('Navigating to chapter with path:', path, 'and fragment:', comment.comment_id);
      this.router.navigate(path, { fragment: comment.comment_id }).then(
        success => console.log('Navigation success:', success),
        error => console.error('Navigation error:', error)
      );
    } else if (comment.series_id) {
      // If it's only a series comment, just navigate to the series
      const path = ['/series', comment.series_id];
      console.log('Navigating to series with path:', path);
      this.router.navigate(path).then(
        success => console.log('Navigation success:', success),
        error => console.error('Navigation error:', error)
      );
    } else {
      console.warn('Cannot navigate - missing series_id');
    }
  }
}
