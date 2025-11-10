import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslatorService } from '../../../services/translator.service';
import { TranslationJobPreview, TranslatedChapterCache, ImportTranslationRequest } from '../../../models/translator';

@Component({
  selector: 'app-job-preview',
  imports: [CommonModule, FormsModule],
  templateUrl: './job-preview.html',
  styleUrl: './job-preview.css',
  standalone: true,
})
export class JobPreview implements OnInit {
  preview?: TranslationJobPreview;
  allChapters: TranslatedChapterCache[] = [];
  selectedChapterNumbers: number[] = [];
  selectedChapter?: TranslatedChapterCache;
  
  // Import form data
  showImportDialog = false;
  coverImageUrl = '';
  seriesStatus: 'Ongoing' | 'Completed' | 'Hiatus' = 'Ongoing';
  
  isLoading = false;
  isImporting = false;
  errorMessage = '';
  viewMode: 'preview' | 'full-chapter' = 'preview';

  constructor(
    private translatorService: TranslatorService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    const jobId = this.route.snapshot.paramMap.get('id');
    if (jobId) {
      this.loadPreview(jobId);
      this.loadAllChapters(jobId);
    }
  }

  loadPreview(jobId: string): void {
    this.isLoading = true;
    this.errorMessage = '';

    // First get the full job to access cover_image_url
    this.translatorService.getJob(jobId).subscribe({
      next: (job) => {
        // Pre-fill cover image URL from scraped data if available
        if (job.cover_image_url) {
          this.coverImageUrl = job.cover_image_url;
        }
      },
      error: (error) => {
        console.error('Error loading job for cover image:', error);
      }
    });

    this.translatorService.getJobPreview(jobId).subscribe({
      next: (data) => {
        this.preview = data;
        // Select all polished chapters by default
        this.selectedChapterNumbers = data.chapters
          .filter(ch => ch.status === 'polished')
          .map(ch => ch.chapter_number);
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load preview';
        this.isLoading = false;
        console.error('Error loading preview:', error);
      }
    });
  }

  loadAllChapters(jobId: string): void {
    this.translatorService.getJobChapters(jobId).subscribe({
      next: (data) => {
        this.allChapters = data.filter(ch => ch.status === 'polished');
      },
      error: (error) => {
        console.error('Error loading chapters:', error);
      }
    });
  }

  toggleChapterSelection(chapterNumber: number): void {
    const index = this.selectedChapterNumbers.indexOf(chapterNumber);
    if (index > -1) {
      this.selectedChapterNumbers.splice(index, 1);
    } else {
      this.selectedChapterNumbers.push(chapterNumber);
    }
  }

  isChapterSelected(chapterNumber: number): boolean {
    return this.selectedChapterNumbers.includes(chapterNumber);
  }

  selectAllChapters(): void {
    if (this.preview) {
      this.selectedChapterNumbers = this.preview.chapters
        .filter(ch => ch.status === 'polished')
        .map(ch => ch.chapter_number);
    }
  }

  deselectAllChapters(): void {
    this.selectedChapterNumbers = [];
  }

  viewChapterContent(chapterNumber: number): void {
    this.selectedChapter = this.allChapters.find(ch => ch.chapter_number === chapterNumber);
    if (this.selectedChapter) {
      this.viewMode = 'full-chapter';
    }
  }

  closeChapterView(): void {
    this.viewMode = 'preview';
    this.selectedChapter = undefined;
  }

  openImportDialog(): void {
    if (this.selectedChapterNumbers.length === 0) {
      alert('Please select at least one chapter to import');
      return;
    }
    this.showImportDialog = true;
  }

  closeImportDialog(): void {
    this.showImportDialog = false;
  }

  importToLibrary(): void {
    if (!this.preview) return;

    if (this.selectedChapterNumbers.length === 0) {
      alert('Please select at least one chapter to import');
      return;
    }

    this.isImporting = true;
    this.errorMessage = '';

    const request: ImportTranslationRequest = {
      status: this.seriesStatus,
      selected_chapters: this.selectedChapterNumbers.sort((a, b) => a - b)
    };

    if (this.coverImageUrl) {
      request.cover_image_url = this.coverImageUrl;
    }

    this.translatorService.importToLibrary(this.preview.job_id, request).subscribe({
      next: (response) => {
        alert(`Successfully imported "${response.series_title}" to library!\n${response.chapters_imported} chapters imported.`);
        this.router.navigate(['/series', response.series_id]);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || 'Failed to import to library';
        this.isImporting = false;
        console.error('Error importing:', error);
      }
    });
  }

  goBack(): void {
    if (this.preview) {
      this.router.navigate(['/staff/translator/job', this.preview.job_id]);
    } else {
      this.router.navigate(['/staff/translator']);
    }
  }

  getTotalWordCount(): number {
    if (!this.preview) return 0;
    return this.preview.chapters
      .filter(ch => this.isChapterSelected(ch.chapter_number))
      .reduce((sum, ch) => sum + (ch.word_count || 0), 0);
  }
}
