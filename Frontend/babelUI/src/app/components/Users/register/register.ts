import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { UserService } from '../../../services/user.service';
import { RegisterData } from '../../../models/user';

@Component({
  selector: 'app-register',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register implements OnInit {
  registerData: RegisterData = {
    username: '',
    email: '',
    password: '',
    role: ''  // Will be set to 'Reader' by default on initialization
  };
  confirmPassword = '';
  error: string | null = null;
  loading = false;

  constructor(
    private authService: AuthService,
    private userService: UserService, // Injected UserService
    private router: Router
  ) {}

  ngOnInit(): void {
    // Set default role to 'Reader' on component initialization
    this.userService.getReaderRole().subscribe({
      next: (readerRole) => {
        if (readerRole) {
          this.registerData.role = readerRole.role_id;
        }
      },
      error: (err) => {
        console.error('Could not fetch default reader role', err);
        this.error = 'Could not initialize registration form. Please try again later.';
      }
    });
  }

  onSubmit(): void {
    if (!this.registerData.username || !this.registerData.email || !this.registerData.password) {
      this.error = 'Please fill in all fields';
      return;
    }

    if (this.registerData.password !== this.confirmPassword) {
      this.error = 'Passwords do not match';
      return;
    }

    if (this.registerData.password.length < 8) {
      this.error = 'Password must be at least 8 characters long';
      return;
    }

    this.loading = true;
    this.error = null;

    // Use userService.createUser for registration
    this.userService.createUser(this.registerData).subscribe({
      next: (response) => {
        // Store authentication tokens and user data from registration response
        this.authService.setAuthResponse(response);
        this.loading = false;

        // Navigate to home page
        this.router.navigate(['/']);
      },
      error: (err) => {
        console.error('Registration error:', err);
        this.error = err.error?.detail || err.error?.username?.[0] || err.error?.email?.[0] || 'Registration failed. Please try again.';
        this.loading = false;
      }
    });
  }
}