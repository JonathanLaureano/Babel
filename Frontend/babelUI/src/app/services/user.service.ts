import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { User, UpdateUserRequest, Role, RegisterData, AuthResponse} from '../models/user';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://localhost:8000/api'; // Adjust this to match your backend URL


  constructor(private http: HttpClient, private authService: AuthService) { }

  /**
   * Get all users (only available to staff)
   */
  getUsers(): Observable<User[]> {
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser?.is_staff) {
      // Return an empty array or an observable with an error if the user is not staff
      console.warn('getUsers() called by a non-staff user. Aborting request.');
      return of([]); // Return an empty array to prevent unauthorized calls
    }
    return this.http.get<User[]>(`${this.apiUrl}/users/`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get a single user by ID
   */
  getUser(userId: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/users/${userId}/`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Get all roles
   */
  getRoles(): Observable<Role[]> {
    return this.http.get<Role[]>(`${this.apiUrl}/roles/`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get the Reader role (to use as default for new users)
   */
  getReaderRole(): Observable<Role | undefined> {
    return this.http.get<Role[]>(`${this.apiUrl}/roles/`)
      .pipe(
        map(roles => roles.find(role => role.name === 'Reader')),
        catchError(this.handleError)
      );
  }

  /**
   * Create a new user with Reader role by default
   */
  createUser(userRequest: RegisterData): Observable<AuthResponse> {
    // Backend returns JWT tokens along with user data upon successful registration
    return this.http.post<AuthResponse>(`${this.apiUrl}/users/`, userRequest)
      .pipe(catchError(this.handleError));
  }

  /**
   * Update an existing user
   */
  updateUser(userId: string, userRequest: UpdateUserRequest): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/users/${userId}/`, userRequest)
      .pipe(catchError(this.handleError));
  }

  /**
   * Delete a user
   */
  deleteUser(userId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/users/${userId}/`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Deactivate a user (soft delete)
   */
  deactivateUser(userId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/users/${userId}/deactivate/`, {})
      .pipe(catchError(this.handleError));
  }

  /**
   * Activate a user
   */
  activateUser(userId: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/users/${userId}/activate/`, {})
      .pipe(catchError(this.handleError));
  }

  /**
   * Set/change user password
   */
  setPassword(userId: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/users/${userId}/set_password/`, { password })
      .pipe(catchError(this.handleError));
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Server Error (${error.status}): ${error.message}`;
      if (error.error && typeof error.error === 'object') {
        // If the backend returns validation errors
        const validationErrors = Object.entries(error.error)
          .map(([key, value]) => `${key}: ${value}`)
          .join(', ');
        if (validationErrors) {
          errorMessage += ` - ${validationErrors}`;
        }
      }
    }
    
    console.error('HTTP Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
