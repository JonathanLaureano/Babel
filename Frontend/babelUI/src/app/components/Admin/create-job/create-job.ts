import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TranslatorService } from '../../../services/translator.service';
import { CreateTranslationJobRequest } from '../../../models/translator';

@Component({
  selector: 'app-create-job',
  imports: [CommonModule, FormsModule],
  templateUrl: './create-job.html',
  styleUrl: './create-job.css',
  standalone: true,
})
export class CreateJob {
  novelUrl = '';
  chaptersRequested = 5;
  translateAll = false;
  isSubmitting = false;
  errorMessage = '';

  constructor(
    private translatorService: TranslatorService,
    private router: Router
  ) {}

  createJob(): void {
    if (!this.novelUrl) {
      this.errorMessage = 'Please enter a valid novel URL';
      return;
    }

    if (!this.translateAll && this.chaptersRequested < 1) {
      this.errorMessage = 'Please enter a valid number of chapters';
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = '';

    const request: CreateTranslationJobRequest = {
      novel_url: this.novelUrl,
      ...(this.translateAll
        ? { translate_all: true }
        : { chapters_requested: this.chaptersRequested })
    };

    this.translatorService.createJob(request).subscribe({
      next: (job) => {
        this.router.navigate(['/staff/translator/job', job.job_id]);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || 'Failed to create translation job';
        this.isSubmitting = false;
        console.error('Error creating job:', error);
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/staff/translator']);
  }
}
