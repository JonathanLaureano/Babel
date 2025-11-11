import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { User, LoginCredentials, AuthResponse } from '../models/user';
import { environment } from '../../environments/environment';
import { SocialAuthService, SocialUser } from '@abacritt/angularx-social-login';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/users`;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    private socialAuthService: SocialAuthService
  ) {
    this.loadUserFromStorage();
  }

  private loadUserFromStorage(): void {
    const userId = sessionStorage.getItem('currentUserId');
    if (userId) {
      // Fetch user details from backend instead of storing full user object
      this.http.get<User>(`${this.apiUrl}/${userId}/`)
        .subscribe({
          next: (user) => {
            this.currentUserSubject.next(user);
          },
          error: (err) => {
            console.error('Failed to load user from storage:', err);
            // Clear invalid user ID
            sessionStorage.removeItem('currentUserId');
          }
        });
    }
  }

  login(credentials: LoginCredentials): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login/`, credentials).pipe(
      tap(response => this.setAuthResponse(response))
    );
  }

  setAuthResponse(response: AuthResponse): void {
    sessionStorage.setItem('access_token', response.access);
    sessionStorage.setItem('refresh_token', response.refresh);
    sessionStorage.setItem('currentUserId', response.user.user_id);
    this.currentUserSubject.next(response.user);
  }

  logout(): void {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('currentUserId');
    sessionStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }

  isLoggedIn(): boolean {
    return !!sessionStorage.getItem('access_token');
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getToken(): string | null {
    return sessionStorage.getItem('access_token');
  }

  updateCurrentUser(user: User): void {
    sessionStorage.setItem('currentUserId', user.user_id);
    this.currentUserSubject.next(user);
  }

  // Google OAuth methods
  googleLogin(googleUser: SocialUser): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/google-login/`, {
      token: googleUser.idToken
    }).pipe(
      tap(response => this.setAuthResponse(response))
    );
  }

  googleRegister(googleUser: SocialUser): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/google-register/`, {
      token: googleUser.idToken
    }).pipe(
      tap(response => this.setAuthResponse(response))
    );
  }
}
