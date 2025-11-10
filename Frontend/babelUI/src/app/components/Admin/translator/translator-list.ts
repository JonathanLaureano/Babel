import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { TranslatorService } from '../../../services/translator.service';
import { TranslationJob } from '../../../models/translator';
import { interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-translator-list',
  imports: [CommonModule],
  templateUrl: './translator-list.html',
  styleUrl: './translator-list.css',
  standalone: true,
})
export class TranslatorList implements OnInit, OnDestroy {
  jobs: TranslationJob[] = [];
  isLoading = false;
  errorMessage = '';
  autoRefresh = true;
  private refreshSubscription?: Subscription;

  constructor(
    private translatorService: TranslatorService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadJobs();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.stopAutoRefresh();
  }

  loadJobs(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.translatorService.getJobs().subscribe({
      next: (data) => {
        this.jobs = data.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load translation jobs';
        this.isLoading = false;
        console.error('Error loading jobs:', error);
      }
    });
  }

  startAutoRefresh(): void {
    if (this.autoRefresh) {
      this.refreshSubscription = interval(3000)
        .pipe(switchMap(() => this.translatorService.getJobs()))
        .subscribe({
          next: (data) => {
            this.jobs = data.sort((a, b) => 
              new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );
          },
          error: (error) => {
            console.error('Auto-refresh error:', error);
          }
        });
    }
  }

  stopAutoRefresh(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
  }

  toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;
    if (this.autoRefresh) {
      this.startAutoRefresh();
    } else {
      this.stopAutoRefresh();
    }
  }

  createJob(): void {
    this.router.navigate(['/staff/translator/create']);
  }

  viewJob(jobId: string): void {
    this.router.navigate(['/staff/translator/job', jobId]);
  }

  previewJob(jobId: string): void {
    this.router.navigate(['/staff/translator/preview', jobId]);
  }

  deleteJob(jobId: string): void {
    if (confirm('Are you sure you want to delete this translation job?')) {
      this.translatorService.deleteJob(jobId).subscribe({
        next: () => {
          this.loadJobs();
        },
        error: (error) => {
          this.errorMessage = 'Failed to delete job. ' + (error.error?.error || '');
          console.error('Error deleting job:', error);
        }
      });
    }
  }

  getStatusClass(status: string): string {
    const statusClasses: { [key: string]: string } = {
      'pending': 'status-pending',
      'scraping': 'status-progress',
      'translating': 'status-progress',
      'completed': 'status-completed',
      'failed': 'status-failed'
    };
    return statusClasses[status] || '';
  }

  getStatusIcon(status: string): string {
    const statusIcons: { [key: string]: string } = {
      'pending': '⏳',
      'scraping': '🔍',
      'translating': '🔄',
      'completed': '✅',
      'failed': '❌'
    };
    return statusIcons[status] || '❓';
  }

  isJobInProgress(job: TranslationJob): boolean {
    return job.status === 'pending' || job.status === 'scraping' || job.status === 'translating';
  }

  canPreview(job: TranslationJob): boolean {
    return job.status === 'completed' || (job.chapters_completed > 0 && job.status === 'translating');
  }

  canDelete(job: TranslationJob): boolean {
    return !job.imported_series;
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }
}
