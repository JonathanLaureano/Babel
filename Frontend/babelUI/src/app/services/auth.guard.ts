import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean {
    
    const currentUser = this.authService.getCurrentUser();
    
    // Check if user is logged in
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return false;
    }
    
    // Check if user is staff for staff-only routes
    const isStaffRoute = state.url.startsWith('/staff');
    
    if (isStaffRoute && (!currentUser || !currentUser.is_staff)) {
      // Redirect to homepage or a general access denied page
      this.router.navigate(['/']);
      return false;
    }
    
    return true;
  }
}