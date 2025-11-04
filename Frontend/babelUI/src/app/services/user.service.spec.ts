import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UserService } from './user.service';
import { User, UpdateUserRequest } from '../models/user';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;
  const apiUrl = 'http://localhost:8000/api/users';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [UserService]
    });
    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get all users', () => {
    const mockUsers: User[] = [
      {
        user_id: '123',
        username: 'testuser',
        email: 'test@example.com',
        role: 'role-id',
        role_name: 'Reader',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];

    service.getUsers().subscribe(users => {
      expect(users.length).toBe(1);
      expect(users).toEqual(mockUsers);
    });

    const req = httpMock.expectOne(`${apiUrl}/`);
    expect(req.request.method).toBe('GET');
    req.flush(mockUsers);
  });

  it('should create a user', () => {
    const createRequest: CreateUserRequest = {
      username: 'newuser',
      email: 'new@example.com',
      password: 'password123'
    };

    const mockUser: User = {
      user_id: '123',
      username: 'newuser',
      email: 'new@example.com',
      role: 'reader-role-id',
      role_name: 'Reader',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    service.createUser(createRequest).subscribe(user => {
      expect(user).toEqual(mockUser);
    });

    const req = httpMock.expectOne(`${apiUrl}/`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(createRequest);
    req.flush(mockUser);
  });

  it('should update a user', () => {
    const userId = '123';
    const updateRequest: UpdateUserRequest = {
      username: 'updateduser',
      email: 'updated@example.com'
    };

    const mockUser: User = {
      user_id: userId,
      username: 'updateduser',
      email: 'updated@example.com',
      role: 'role-id',
      role_name: 'Reader',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    service.updateUser(userId, updateRequest).subscribe(user => {
      expect(user).toEqual(mockUser);
    });

    const req = httpMock.expectOne(`${apiUrl}/${userId}/`);
    expect(req.request.method).toBe('PATCH');
    expect(req.request.body).toEqual(updateRequest);
    req.flush(mockUser);
  });

  it('should delete a user', () => {
    const userId = '123';

    service.deleteUser(userId).subscribe(response => {
      expect(response).toBeUndefined();
    });

    const req = httpMock.expectOne(`${apiUrl}/${userId}/`);
    expect(req.request.method).toBe('DELETE');
    req.flush(null);
  });
});
