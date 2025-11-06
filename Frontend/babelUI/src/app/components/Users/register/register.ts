import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { UserService } from '../../../services/user.service';
import { RegisterData, Role } from '../../../models/user';

@Component({
  selector: 'app-register',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  registerData = {
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  };
  error: string | null = null;
  loading = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (!this.registerData.username || !this.registerData.email || !this.registerData.password) {
      this.error = 'Please fill in all fields';
      return;
    }

    if (this.registerData.password !== this.registerData.confirmPassword) {
      this.error = 'Passwords do not match';
      return;
    }

    if (this.registerData.password.length < 8) {
      this.error = 'Password must be at least 8 characters long';
      return;
    }

    this.loading = true;
    this.error = null;

    const { confirmPassword, ...data } = this.registerData;

    this.authService.register(data).subscribe({
      next: () => {
        // Auto-login after registration
        this.authService.login({
          username: data.username,
          password: data.password
        }).subscribe({
          next: () => {
            this.router.navigate(['/']);
          },
          error: (err) => {
            console.error('Auto-login error:', err);
            this.router.navigate(['/login']);
          }
        });
      },
      error: (err) => {
        console.error('Registration error:', err);
        this.error = err.error?.detail || err.error?.username?.[0] || err.error?.email?.[0] || 'Registration failed. Please try again.';
        this.loading = false;
      }
    });
  }
}