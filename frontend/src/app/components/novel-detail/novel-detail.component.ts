import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { NovelService } from '../../services/novel.service';
import { Novel, Chapter } from '../../models/novel';

@Component({
  selector: 'app-novel-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './novel-detail.component.html',
  styleUrl: './novel-detail.component.css'
})
export class NovelDetailComponent implements OnInit {
  novel: Novel | null = null;
  chapters: Chapter[] = [];
  loading = false;
  error = '';

  constructor(
    private route: ActivatedRoute,
    private novelService: NovelService
  ) { }

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.loadNovel(id);
      this.loadChapters(id);
    }
  }

  loadNovel(id: number): void {
    this.loading = true;
    this.novelService.getNovel(id).subscribe({
      next: (data) => {
        this.novel = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load novel';
        this.loading = false;
        console.error(err);
      }
    });
  }

  loadChapters(novelId: number): void {
    this.novelService.getChapters(novelId).subscribe({
      next: (data) => {
        this.chapters = data;
      },
      error: (err) => {
        console.error('Failed to load chapters', err);
      }
    });
  }
}

