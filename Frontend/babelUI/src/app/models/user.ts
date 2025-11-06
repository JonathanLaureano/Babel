export interface Role {
  role_id: string;
  name: string;
  description?: string;
}

export interface User {
  user_id: string;
  username: string;
  email: string;
  role: string; // Role ID
  role_name?: string; // Read-only, populated by backend
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  role?: string;
}

export interface UpdateUserRequest {
  username?: string;
  email?: string;
  password?: string;
  role?: string;
  is_active?: boolean;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}