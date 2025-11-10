import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { LibraryService } from '../../../services/library.service';
import { UserService } from '../../../services/user.service';
import { Series } from '../../../models/series';
import { ChapterListItem } from '../../../models/chapter';
import { User } from '../../../models/user';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-admin',
  imports: [CommonModule],
  templateUrl: './admin.html',
  styleUrl: './admin.css',
  standalone: true,
})
export class Admin implements OnInit {
  activeTab: 'series' | 'chapters' | 'users' | 'translator' = 'series';
  
  series: Series[] = [];
  chapters: ChapterListItem[] = [];
  users: User[] = [];
  
  isLoading = false;
  errorMessage = '';

  constructor(
    private libraryService: LibraryService,
    private userService: UserService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  setActiveTab(tab: 'series' | 'chapters' | 'users' | 'translator'): void {
    this.activeTab = tab;
    if (tab === 'translator') {
      this.router.navigate(['/staff/translator']);
    } else {
      this.loadData();
    }
  }

  loadData(): void {
    this.isLoading = true;
    this.errorMessage = '';

    if (this.activeTab === 'series') {
      this.loadSeries();
    } else if (this.activeTab === 'chapters') {
      this.loadChapters();
    } else if (this.activeTab === 'users') {
      this.loadUsers();
    }
  }

  loadSeries(): void {
    this.libraryService.getSeries().subscribe({
      next: (data) => {
        data.sort((a, b) => a.title.localeCompare(b.title));
        this.series = data;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load series';
        this.isLoading = false;
        console.error('Error loading series:', error);
      }
    });
  }

  loadChapters(): void {
    this.libraryService.getSeries().subscribe({
      next: (seriesData) => {
        if (seriesData.length === 0) {
          this.chapters = [];
          this.isLoading = false;
          return;
        }
        const chapterRequests = seriesData.map(s => 
          this.libraryService.getSeriesChapters(s.series_id)
        );
        
        forkJoin(chapterRequests).subscribe({
          next: (results) => {
            const flatChapters = results.flat();
            flatChapters.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
            this.chapters = flatChapters;
            this.isLoading = false;
          },
          error: (error) => {
            this.errorMessage = 'Failed to load chapters';
            this.isLoading = false;
            console.error('Error loading chapters:', error);
          }
        });
      },
      error: (error) => {
        this.errorMessage = 'Failed to load series for chapters';
        this.isLoading = false;
        console.error('Error loading chapters:', error);
      }
    });
  }

  loadUsers(): void {
    this.userService.getUsers().subscribe({
      next: (data) => {
        this.users = data;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Failed to load users';
        this.isLoading = false;
        console.error('Error loading users:', error);
      }
    });
  }

  // Series actions
  addSeries(): void {
    this.router.navigate(['/staff/add-series']);
  }

  editSeries(seriesId: string): void {
    this.router.navigate(['/staff/edit-series', seriesId]);
  }

  addChapter(seriesId: string): void {
    this.router.navigate(['/staff/add-chapter', seriesId]);
  }

  deleteSeries(seriesId: string): void {
    if (confirm('Are you sure you want to delete this series and all its chapters?')) {
      this.libraryService.deleteSeries(seriesId).subscribe({
        next: () => this.loadSeries(),
        error: (err) => {
          this.errorMessage = 'Failed to delete series.';
          console.error(err);
        }
      });
    }
  }

  // Chapter actions
  editChapter(chapterId: string): void {
    this.router.navigate(['/staff/edit-chapter', chapterId]);
  }

  deleteChapter(chapterId: string): void {
    if (confirm('Are you sure you want to delete this chapter?')) {
      this.libraryService.deleteChapter(chapterId).subscribe({
        next: () => this.loadChapters(),
        error: (err) => {
          this.errorMessage = 'Failed to delete chapter.';
          console.error(err);
        }
      });
    }
  }

  // User actions
  viewUserInfo(userId: string): void {
    //TODO: This could navigate to a user detail page if one exists
    console.log('View Information clicked:', userId);
  }

  deleteUser(userId: string): void {
    if (confirm('Are you sure you want to delete this user?')) {
      this.userService.deleteUser(userId).subscribe({
        next: () => this.loadUsers(),
        error: (err) => {
          this.errorMessage = 'Failed to delete user.';
          console.error(err);
        }
      });
    }
  }
}
