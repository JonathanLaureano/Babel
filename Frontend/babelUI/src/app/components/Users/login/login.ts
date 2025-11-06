import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { LoginCredentials } from '../../../models/user';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
  standalone: true,
})
export class Login {
  credentials: LoginCredentials = {
    username: '',
    password: ''
  };
  error: string | null = null;
  loading = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  login(): void {
    if (!this.credentials.username || !this.credentials.password) {
      this.error = 'Username and password are required';
      return;
    }

    this.loading = true;
    this.error = null;

    console.log('Attempting login with username:', this.credentials.username);
    this.authService.login(this.credentials).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (err: any) => {
        console.error('Login failed:', err);
        this.error = err.error?.detail || 'Invalid username or password';
        this.loading = false;
      }
    });
  }
}