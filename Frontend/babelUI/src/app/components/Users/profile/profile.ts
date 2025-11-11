import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { UserService } from '../../../services/user.service';
import { User } from '../../../models/user';
import { ProfileInfoTab } from './profile-info/profile-info-tab';
import { CommentsTab } from './comments/comments-tab';
import { BookmarksTab } from './bookmarks/bookmarks-tab';

type TabType = 'info' | 'comments' | 'bookmarks';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, ProfileInfoTab, CommentsTab, BookmarksTab],
  templateUrl: './profile.html',
  styleUrl: './profile.css',
  standalone: true,
})
export class Profile implements OnInit {
  user: User | null = null;
  activeTab: TabType = 'info';
  error: string | null = null;
  success: string | null = null;
  loading = false;

  constructor(
    private authService: AuthService,
    private userService: UserService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    if (!this.user) {
      this.router.navigate(['/login']);
      return;
    }
  }

  switchTab(tab: TabType): void {
    this.activeTab = tab;
    this.error = null;
    this.success = null;
  }

  updateProfile(editData: { username: string; email: string }): void {
    if (!this.user) {
      return;
    }

    // Validate changes
    if (!editData.username || !editData.email) {
      this.error = 'Username and email are required';
      return;
    }

    // Check if anything actually changed
    if (editData.username === this.user.username && 
        editData.email === this.user.email) {
      this.success = 'No changes to save';
      return;
    }

    this.loading = true;
    this.error = null;
    this.success = null;

    this.userService.updateUser(this.user.user_id, editData).subscribe({
      next: (updatedUser: User) => {
        this.user = updatedUser;
        this.authService.updateCurrentUser(updatedUser);
        this.success = 'Profile updated successfully!';
        this.loading = false;
      },
      error: (err: any) => {
        console.error('Update profile error:', err);
        this.error = err.message || 'Failed to update profile';
        this.loading = false;
      }
    });
  }

  deleteProfile(): void {
    if (!this.user) {
      return;
    }

    this.loading = true;
    this.error = null;

    this.userService.deleteUser(this.user.user_id).subscribe({
      next: () => {
        this.authService.logout();
        this.router.navigate(['/']);
      },
      error: (err: any) => {
        console.error('Delete profile error:', err);
        this.error = err.message || 'Failed to delete account';
        this.loading = false;
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
