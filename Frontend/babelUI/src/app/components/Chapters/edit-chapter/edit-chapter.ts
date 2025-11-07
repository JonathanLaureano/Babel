import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { Chapter } from '../../../models/chapter';

@Component({
  selector: 'app-edit-chapter',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './edit-chapter.html',
  styleUrls: ['./edit-chapter.css']
})
export class EditChapter implements OnInit {
  chapter: Chapter | null = null;
  chapterUpdateData = {
    chapter_number: 1,
    title: '',
    content: '',
  };
  error: string | null = null;
  loading = true;
  chapterId: string | null = null;

  constructor(
    private libraryService: LibraryService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.chapterId = this.route.snapshot.paramMap.get('id');
    if (!this.chapterId) {
      this.error = "Chapter ID not found.";
      this.loading = false;
      return;
    }

    this.libraryService.getChapter(this.chapterId).subscribe({
      next: (chapter) => {
        this.chapter = chapter;
        this.chapterUpdateData = {
          chapter_number: chapter.chapter_number,
          title: chapter.title,
          content: chapter.content
        };
        this.loading = false;
      },
      error: (err) => {
        this.error = "Failed to load chapter data.";
        this.loading = false;
        console.error(err);
      }
    });
  }

  onSubmit(): void {
    if (!this.chapterId) return;
    this.loading = true;
    this.error = null;
    this.libraryService.updateChapter(this.chapterId, this.chapterUpdateData).subscribe({
      next: () => {
        this.router.navigate(['/staff']);
      },
      error: (err) => {
        this.error = 'Failed to update chapter.';
        this.loading = false;
        console.error(err);
      }
    });
  }
}
