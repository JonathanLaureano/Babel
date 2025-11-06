import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { UserService } from '../../services/user.service';
import { User } from '../../models/user';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {
  user: User | null = null;
  isEditing = false;
  editData = {
    username: '',
    email: ''
  };
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
    this.editData = {
      username: this.user.username,
      email: this.user.email
    };
  }

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    this.error = null;
    this.success = null;
    if (!this.isEditing && this.user) {
      this.editData = {
        username: this.user.username,
        email: this.user.email
      };
    }
  }

  updateProfile(): void {
    if (!this.user) {
      return;
    }

    // Validate changes
    if (!this.editData.username || !this.editData.email) {
      this.error = 'Username and email are required';
      return;
    }

    // Check if anything actually changed
    if (this.editData.username === this.user.username && 
        this.editData.email === this.user.email) {
      this.success = 'No changes to save';
      this.isEditing = false;
      return;
    }

    this.loading = true;
    this.error = null;
    this.success = null;

    this.userService.updateUser(this.user.user_id, this.editData).subscribe({
      next: (updatedUser) => {
        this.user = updatedUser;
        // Use the AuthService to update the current user, ensuring the observable is updated
        this.authService.updateCurrentUser(updatedUser);
        this.success = 'Profile updated successfully!';
        this.isEditing = false;
        this.loading = false;
      },
      error: (err) => {
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

    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    this.loading = true;
    this.error = null;

    this.userService.deleteUser(this.user.user_id).subscribe({
      next: () => {
        // Logout and redirect
        this.authService.logout();
        alert('Your account has been successfully deleted.');
        this.router.navigate(['/']);
      },
      error: (err) => {
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
