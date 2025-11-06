import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UserService } from './user.service';
import { User, UpdateUserRequest, RegisterData, Role } from '../models/user';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;
  const apiUrl = 'http://localhost:8000/api/users';
  const rolesUrl = 'http://localhost:8000/api/roles';

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

  it('should get a single user by ID', () => {
    const userId = '123';
    const mockUser: User = {
      user_id: userId,
      username: 'testuser',
      email: 'test@example.com',
      role: 'role-id',
      role_name: 'Reader',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    service.getUser(userId).subscribe(user => {
      expect(user).toEqual(mockUser);
    });

    const req = httpMock.expectOne(`${apiUrl}/${userId}/`);
    expect(req.request.method).toBe('GET');
    req.flush(mockUser);
  });

  it('should get all roles', () => {
    const mockRoles: Role[] = [
      { role_id: '1', name: 'Admin', description: 'Administrator' },
      { role_id: '2', name: 'Reader', description: 'Reader' }
    ];

    service.getRoles().subscribe(roles => {
      expect(roles.length).toBe(2);
      expect(roles).toEqual(mockRoles);
    });

    const req = httpMock.expectOne(`${rolesUrl}/`);
    expect(req.request.method).toBe('GET');
    req.flush(mockRoles);
  });

  it('should get the Reader role', () => {
    const mockRoles: Role[] = [
      { role_id: '1', name: 'Admin', description: 'Administrator' },
      { role_id: '2', name: 'Reader', description: 'Reader' }
    ];
    const readerRole = mockRoles[1];

    service.getReaderRole().subscribe(role => {
      expect(role).toEqual(readerRole);
    });

    const req = httpMock.expectOne(`${rolesUrl}/`);
    expect(req.request.method).toBe('GET');
    req.flush(mockRoles);
  });

  it('should create a user', () => {
    const createRequest: RegisterData = {
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

  it('should deactivate a user', () => {
    const userId = '123';
    service.deactivateUser(userId).subscribe();

    const req = httpMock.expectOne(`${apiUrl}/${userId}/deactivate/`);
    expect(req.request.method).toBe('POST');
    req.flush({});
  });

  it('should activate a user', () => {
    const userId = '123';
    service.activateUser(userId).subscribe();

    const req = httpMock.expectOne(`${apiUrl}/${userId}/activate/`);
    expect(req.request.method).toBe('POST');
    req.flush({});
  });

  it('should set a user password', () => {
    const userId = '123';
    const password = 'newpassword';
    service.setPassword(userId, password).subscribe();

    const req = httpMock.expectOne(`${apiUrl}/${userId}/set_password/`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ password });
    req.flush({});
  });
});
