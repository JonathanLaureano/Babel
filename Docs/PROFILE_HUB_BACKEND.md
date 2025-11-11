# Profile Hub Backend Implementation

This document describes the backend implementation for the Profile Hub feature.

## Overview

The backend provides REST API endpoints for:
- User bookmarks (save favorite series)
- Reading history (track last read chapter per series)
- User comments (enhanced filtering)

## Database Models

### Bookmark Model
**Location:** `users/models.py`

```python
class Bookmark(models.Model):
    bookmark_id = UUIDField (Primary Key)
    user = ForeignKey(User)
    series = ForeignKey(Series)
    created_at = DateTimeField
```

**Features:**
- Unique constraint on (user, series) - one bookmark per series per user
- Indexed on user and series for fast lookups
- Ordered by creation date (newest first)

### ReadingHistory Model
**Location:** `users/models.py`

```python
class ReadingHistory(models.Model):
    history_id = UUIDField (Primary Key)
    user = ForeignKey(User)
    series = ForeignKey(Series)
    chapter = ForeignKey(Chapter)
    last_read_at = DateTimeField (auto_now=True)
    created_at = DateTimeField
```

**Features:**
- Unique constraint on (user, series) - one history record per series per user
- Automatically updates `last_read_at` when the record is modified
- Indexed on user/series and user/last_read_at for efficient queries
- Ordered by last_read_at (most recent first)

## API Endpoints

### Bookmarks API

**Base URL:** `/api/bookmarks/`

#### List/Filter Bookmarks
```http
GET /api/bookmarks/
GET /api/bookmarks/?user={user_id}
GET /api/bookmarks/?series={series_id}
GET /api/bookmarks/?user={user_id}&series={series_id}
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "bookmark_id": "uuid",
      "user": "user_uuid",
      "series": "series_uuid",
      "series_details": {
        "series_id": "uuid",
        "title": "Series Title",
        "author": "Author Name",
        "cover_image_url": "https://...",
        "status": "Ongoing",
        "genres": [...],
        "average_rating": 4.5,
        ...
      },
      "created_at": "2025-11-11T14:30:00Z"
    }
  ]
}
```

#### Create Bookmark
```http
POST /api/bookmarks/
Content-Type: application/json
Authorization: Bearer {token}

{
  "series": "series_uuid"
}
```

**Response:** `201 Created` with bookmark object

#### Delete Bookmark
```http
DELETE /api/bookmarks/{bookmark_id}/
Authorization: Bearer {token}
```

**Response:** `204 No Content`

**Permissions:**
- List: Authenticated users
- Create: Authenticated users (automatically set to current user)
- Delete: Bookmark owner or staff

---

### Reading History API

**Base URL:** `/api/reading-history/`

#### List/Filter Reading History
```http
GET /api/reading-history/
GET /api/reading-history/?user={user_id}
GET /api/reading-history/?series={series_id}
GET /api/reading-history/?user={user_id}&ordering=-last_read_at
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "history_id": "uuid",
      "user": "user_uuid",
      "series": "series_uuid",
      "chapter": "chapter_uuid",
      "series_title": "Series Title",
      "chapter_number": 15,
      "chapter_title": "Chapter Title",
      "last_read_at": "2025-11-11T14:45:00Z",
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

#### Update/Create Reading History
```http
POST /api/reading-history/
Content-Type: application/json
Authorization: Bearer {token}

{
  "series": "series_uuid",
  "chapter": "chapter_uuid"
}
```

**Behavior:**
- Creates new record if user hasn't read this series before
- Updates existing record if user has read this series before
- Automatically updates `last_read_at` timestamp

**Response:** `201 Created` or `200 OK` with history object

**Permissions:**
- List: Authenticated users
- Create/Update: Authenticated users (automatically set to current user)
- No delete endpoint (history is preserved)

---

### Comments API Enhancement

**Added Endpoint:** `/api/comments/by_user/`

#### Get User Comments
```http
GET /api/comments/by_user/?user={user_id}
GET /api/comments/by_user/?user={user_id}&ordering=-created_at
```

**Response:**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "comment_id": "uuid",
      "user": "user_uuid",
      "user_username": "username",
      "text": "Comment text...",
      "content_type_display": "Series",
      "parent_comment": null,
      "like_count": 5,
      "reply_count": 2,
      "is_liked_by_user": false,
      "created_at": "2025-11-11T14:30:00Z",
      "updated_at": "2025-11-11T14:30:00Z"
    }
  ]
}
```

**Features:**
- Filters comments by user
- Supports ordering (default: -created_at)
- Includes like_count and reply_count
- Paginated results

---

## Serializers

### BookmarkSerializer
**Location:** `users/serializers.py`

**Features:**
- Automatically sets user from request context
- Returns nested series details via `series_details` field
- Uses `SeriesSerializer` for complete series information

### ReadingHistorySerializer
**Location:** `users/serializers.py`

**Features:**
- Automatically sets user from request context
- Returns series_title, chapter_number, and chapter_title as read-only fields
- Uses `update_or_create` to ensure one record per user/series
- Auto-updates `last_read_at` timestamp

---

## ViewSets

### BookmarkViewSet
**Location:** `users/views.py`

**Features:**
- Filters by user and/or series via query parameters
- Optimized with `select_related` for user and series
- Automatic user assignment on create
- Permission checks for deletion (owner or staff)

### ReadingHistoryViewSet
**Location:** `users/views.py`

**Features:**
- Filters by user and/or series via query parameters
- Supports custom ordering via query parameter
- Optimized with `select_related` for user, series, and chapter
- Automatic user assignment on create
- Update-or-create logic for upsert behavior
- Read-only for HTTP methods (no PUT/PATCH/DELETE)

---

## URL Routes

All routes are registered in `users/urls.py`:

```python
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
router.register(r'reading-history', ReadingHistoryViewSet, basename='reading-history')
```

**Available URLs:**
- `/api/bookmarks/` (GET, POST)
- `/api/bookmarks/{bookmark_id}/` (GET, DELETE)
- `/api/reading-history/` (GET, POST)
- `/api/reading-history/{history_id}/` (GET)
- `/api/comments/by_user/` (GET)

---

## Database Migration

**Migration File:** `users/migrations/0004_readinghistory_bookmark.py`

**Created Tables:**
- `bookmark` - stores user bookmarks
- `readinghistory` - tracks reading progress

**Indexes Created:**
- `bookmark(user, series)` - for fast lookups
- `readinghistory(user, series)` - for fast lookups
- `readinghistory(user, -last_read_at)` - for recent history queries

**To Apply Migration:**
```bash
cd Backend
source venv/bin/activate
cd babelLibrary
python manage.py migrate
```

---

## Security & Permissions

### Authentication
All endpoints require authentication (JWT Bearer token) except:
- Comments by_user endpoint (read-only, can be public)

### Authorization
- **Bookmarks:** Users can only create/delete their own bookmarks
- **Reading History:** Users can only create/update their own history
- **Staff Override:** Staff users can delete any bookmark

### Data Privacy
- Users can only query their own data by default
- Query parameters allow filtering, but authentication is required
- No user can modify another user's bookmarks or history

---

## Testing the API

### Create a Bookmark
```bash
curl -X POST http://localhost:8000/api/bookmarks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"series": "SERIES_UUID"}'
```

### Get User Bookmarks
```bash
curl http://localhost:8000/api/bookmarks/?user=USER_UUID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Reading History
```bash
curl -X POST http://localhost:8000/api/reading-history/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"series": "SERIES_UUID", "chapter": "CHAPTER_UUID"}'
```

### Get User Comments
```bash
curl "http://localhost:8000/api/comments/by_user/?user=USER_UUID&ordering=-created_at" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Integration with Frontend

The backend is fully compatible with the Angular frontend implementation. The frontend expects:

1. **Bookmark endpoints** matching the structure defined above
2. **Reading history endpoints** for tracking and resuming
3. **Comment filtering** by user for the comments tab

All response formats match the TypeScript interfaces defined in the frontend.

---

## Performance Considerations

1. **Database Queries:**
   - All viewsets use `select_related` to avoid N+1 queries
   - Proper indexing on frequently queried fields
   - Pagination enabled by default

2. **Caching:** (Future Enhancement)
   - Consider caching user bookmarks
   - Cache reading history for frequently accessed series

3. **Bulk Operations:** (Future Enhancement)
   - Add bulk bookmark creation/deletion
   - Batch reading history updates

---

## Future Enhancements

1. **Bookmark Collections/Folders**
   - Allow users to organize bookmarks into collections
   - Add tags to bookmarks

2. **Reading Statistics**
   - Track total chapters read
   - Calculate reading streaks
   - Generate reading reports

3. **Social Features**
   - Share bookmarks with other users
   - Follow other users' reading lists
   - Bookmark recommendations

4. **Notifications**
   - Notify when bookmarked series have new chapters
   - Alert for replies to user comments
