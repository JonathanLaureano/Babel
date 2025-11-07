import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';

@Component({
  selector: 'app-add-chapter',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './add-chapter.html',
  styleUrls: ['./add-chapter.css']
})
export class AddChapter implements OnInit {
  chapter = {
    series: '',
    chapter_number: 1,
    title: '',
    content: '',
  };
  error: string | null = null;
  loading = true; // Start with loading true

  constructor(
    private libraryService: LibraryService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const seriesId = this.route.snapshot.paramMap.get('seriesId');
    if (seriesId) {
      this.chapter.series = seriesId;
      // Fetch existing chapters to determine the next chapter number
      this.libraryService.getSeriesChapters(seriesId).subscribe({
        next: (chapters) => {
          const lastChapter = chapters.reduce((max, ch) => ch.chapter_number > max ? ch.chapter_number : max, 0);
          this.chapter.chapter_number = lastChapter + 1;
          this.loading = false;
        },
        error: (err) => {
          this.error = "Could not determine the next chapter number.";
          this.loading = false;
          console.error(err);
        }
      });
    } else {
      this.error = "Series ID is missing.";
      this.loading = false;
    }
  }

  onSubmit(): void {
    if (!this.chapter.series) return;
    this.loading = true;
    this.error = null;
    this.libraryService.createChapter(this.chapter).subscribe({
      next: () => {
        this.router.navigate(['/staff']);
      },
      error: (err) => {
        this.error = 'Failed to create chapter.';
        this.loading = false;
        console.error(err);
      }
    });
  }
}
