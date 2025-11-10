import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslatorService } from '../../../services/translator.service';
import { TranslationJob } from '../../../models/translator';
import { interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-job-detail',
  imports: [CommonModule],
  templateUrl: './job-detail.html',
  styleUrl: './job-detail.css',
  standalone: true,
})
export class JobDetail implements OnInit, OnDestroy {
  job?: TranslationJob;
  isLoading = false;
  errorMessage = '';
  private refreshSubscription?: Subscription;

  constructor(
    private translatorService: TranslatorService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    const jobId = this.route.snapshot.paramMap.get('id');
    if (jobId) {
      this.loadJob(jobId);
      this.startAutoRefresh(jobId);
    }
  }

  ngOnDestroy(): void {
    this.stopAutoRefresh();
  }

  loadJob(jobId: string): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.translatorService.getJob(jobId).subscribe({
      next: (data) => {
        this.job = data;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load job details';
        this.isLoading = false;
        console.error('Error loading job:', error);
      }
    });
  }

  startAutoRefresh(jobId: string): void {
    this.refreshSubscription = interval(3000)
      .pipe(switchMap(() => this.translatorService.getJob(jobId)))
      .subscribe({
        next: (data) => {
          this.job = data;
          // Stop auto-refresh if job is completed or failed
          if (data.status === 'completed' || data.status === 'failed') {
            this.stopAutoRefresh();
          }
        },
        error: (error) => {
          console.error('Auto-refresh error:', error);
        }
      });
  }

  stopAutoRefresh(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
  }

  goBack(): void {
    this.router.navigate(['/staff/translator']);
  }

  preview(): void {
    if (this.job) {
      this.router.navigate(['/staff/translator/preview', this.job.job_id]);
    }
  }

  deleteJob(): void {
    if (this.job && confirm('Are you sure you want to delete this job?')) {
      this.translatorService.deleteJob(this.job.job_id).subscribe({
        next: () => {
          this.router.navigate(['/staff/translator']);
        },
        error: (error) => {
          this.errorMessage = 'Failed to delete job. ' + (error.error?.error || '');
          console.error('Error deleting job:', error);
        }
      });
    }
  }

  isInProgress(): boolean {
    return this.job?.status === 'pending' || this.job?.status === 'scraping' || this.job?.status === 'translating';
  }

  canPreview(): boolean {
    return !!this.job && (this.job.status === 'completed' || this.job.chapters_completed > 0);
  }

  canDelete(): boolean {
    return !!this.job && !this.job.imported_series;
  }

  formatDate(dateString?: string): string {
    return dateString ? new Date(dateString).toLocaleString() : '';
  }
}
