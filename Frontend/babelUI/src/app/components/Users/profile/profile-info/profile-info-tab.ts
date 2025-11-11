import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { User } from '../../../../models/user';

@Component({
  selector: 'app-profile-info-tab',
  imports: [CommonModule, FormsModule],
  templateUrl: './profile-info-tab.html',
  styleUrl: './profile-info-tab.css',
  standalone: true,
})
export class ProfileInfoTab implements OnChanges {
  @Input() user: User | null = null;
  @Input() loading = false;
  @Input() error: string | null = null;
  @Input() success: string | null = null;
  @Output() updateProfile = new EventEmitter<{ username: string; email: string }>();
  @Output() deleteProfile = new EventEmitter<void>();
  @Output() logout = new EventEmitter<void>();

  isEditing = false;
  editData = {
    username: '',
    email: ''
  };

  ngOnChanges(): void {
    if (this.user) {
      this.editData = {
        username: this.user.username,
        email: this.user.email
      };
    }
  }

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (!this.isEditing && this.user) {
      this.editData = {
        username: this.user.username,
        email: this.user.email
      };
    }
  }

  onSubmit(): void {
    if (!this.editData.username || !this.editData.email) {
      return;
    }
    this.updateProfile.emit(this.editData);
  }

  onDelete(): void {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      this.deleteProfile.emit();
    }
  }

  onLogout(): void {
    this.logout.emit();
  }
}
