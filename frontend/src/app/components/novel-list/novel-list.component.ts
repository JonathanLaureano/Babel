import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NovelService } from '../../services/novel.service';
import { Novel } from '../../models/novel';

@Component({
  selector: 'app-novel-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './novel-list.component.html',
  styleUrl: './novel-list.component.css'
})
export class NovelListComponent implements OnInit {
  novels: Novel[] = [];
  loading = false;
  error = '';

  constructor(private novelService: NovelService) { }

  ngOnInit(): void {
    this.loadNovels();
  }

  loadNovels(): void {
    this.loading = true;
    this.novelService.getNovels().subscribe({
      next: (data) => {
        this.novels = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load novels';
        this.loading = false;
        console.error(err);
      }
    });
  }
}

