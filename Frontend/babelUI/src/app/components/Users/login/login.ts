import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { LoginCredentials } from '../../../models/user';
import { SocialAuthService, GoogleSigninButtonModule } from '@abacritt/angularx-social-login';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule, RouterLink, GoogleSigninButtonModule],
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
    private router: Router,
    private socialAuthService: SocialAuthService
  ) {
    // Listen for Google sign-in events
    this.socialAuthService.authState.subscribe((user) => {
      if (user) {
        this.handleGoogleLogin(user);
      }
    });
  }

  login(): void {
    if (!this.credentials.username || !this.credentials.password) {
      this.error = 'Username and password are required';
      return;
    }

    this.loading = true;
    this.error = null;

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

  handleGoogleLogin(googleUser: any): void {
    this.loading = true;
    this.error = null;

    this.authService.googleLogin(googleUser).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/']);
      },
      error: (err: any) => {
        console.error('Google login failed:', err);
        this.error = err.error?.detail || 'Google login failed. Please try again.';
        this.loading = false;
      }
    });
  }
}
