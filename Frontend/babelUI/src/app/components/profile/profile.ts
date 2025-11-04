import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
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

  saveProfile(): void {
    // TODO: Implement profile update API call
    this.success = 'Profile update functionality coming soon!';
    this.isEditing = false;
  }

  deleteProfile(): void {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }
    
    // TODO: Implement account deletion API call
    alert('Account deletion functionality coming soon!');
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }
}
