import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Role(models.Model):
    """Defines different user roles within the system."""
    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']  # Add this line to provide a default order

    def __str__(self):
        return self.name


class Permission(models.Model):
    """Lists all possible actions or resources that can be controlled."""
    permission_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'permissions'

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Creates the many-to-many relationship between Roles and Permissions."""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_roles')

    class Meta:
        db_table = 'rolepermissions'
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserManager(BaseUserManager):
    """Custom user manager for User model."""
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Stores basic user information and links to their assigned role."""
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, related_name='users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for Django admin
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    @property
    def id(self):
        """Return user_id as id for compatibility with libraries expecting 'id' attribute"""
        return self.user_id


class Bookmark(models.Model):
    """Stores user bookmarks for series."""
    bookmark_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='bookmarks')
    series = models.ForeignKey('library.Series', on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmark'
        unique_together = ('user', 'series')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'series']),
        ]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.series.title}"


class ReadingHistory(models.Model):
    """Tracks the last read chapter for each user per series."""
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='reading_history')
    series = models.ForeignKey('library.Series', on_delete=models.CASCADE, related_name='read_by')
    chapter = models.ForeignKey('library.Chapter', on_delete=models.CASCADE, related_name='reading_records')
    last_read_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'readinghistory'
        unique_together = ('user', 'series')
        ordering = ['-last_read_at']
        indexes = [
            models.Index(fields=['user', 'series']),
            models.Index(fields=['user', '-last_read_at']),
        ]

    def __str__(self):
        return f"{self.user.username} last read {self.series.title} - Chapter {self.chapter.chapter_number}"
