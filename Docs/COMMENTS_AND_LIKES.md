# Comments App

A Django REST Framework app for managing comments with full CRUD operations, nested replies, and likes.

## Features

- **Comments on Multiple Content Types**: Users can comment on Series, Chapters, and other Users
- **Nested Comments**: Comments can have replies (one level deep)
- **Like System**: Users can like/unlike comments (one like per user per comment)
- **Full CRUD Operations**: Create, Read, Update, and Delete comments
- **Timestamps**: All comments display creation time
- **Authentication**: Read comments publicly, but authentication required for creating, editing, or liking

## Models

### Comment
- `comment_id` (UUID): Primary key
- `user` (FK): The user who created the comment
- `text` (TextField): The comment body
- `content_type` (FK): Generic foreign key for Series/Chapter/User
- `object_id` (UUID): ID of the content being commented on
- `parent_comment` (FK): Optional reference to parent comment for replies
- `created_at` (DateTime): Timestamp when comment was created
- `updated_at` (DateTime): Timestamp when comment was last updated

**Properties:**
- `like_count`: Total number of likes
- `reply_count`: Total number of replies

### CommentLike
- `like_id` (UUID): Primary key
- `comment` (FK): The comment being liked
- `user` (FK): The user who liked the comment
- `created_at` (DateTime): Timestamp when like was created

**Constraint:** A user can only like a comment once (unique together on comment + user)

## API Endpoints

### Comments

#### List Comments
```
GET /api/comments/
```
Returns all comments (paginated).

#### Get Comments by Content
```
GET /api/comments/by_content/?content_type=series&object_id=<uuid>
```
Get all top-level comments for a specific Series, Chapter, or User.

**Query Parameters:**
- `content_type`: `series`, `chapter`, or `user`
- `object_id`: UUID of the content

#### Get Single Comment
```
GET /api/comments/<comment_id>/
```

#### Create Comment
```
POST /api/comments/
```
**Authentication Required**

**Request Body:**
```json
{
  "text": "This is a great series!",
  "content_type": "series",
  "object_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Create Reply
```
POST /api/comments/
```
**Authentication Required**

**Request Body:**
```json
{
  "text": "I agree!",
  "parent_comment": "<parent_comment_id>"
}
```

#### Update Comment
```
PUT /api/comments/<comment_id>/
PATCH /api/comments/<comment_id>/
```
**Authentication Required** (must be comment owner)

**Request Body:**
```json
{
  "text": "Updated comment text"
}
```

#### Delete Comment
```
DELETE /api/comments/<comment_id>/
```
**Authentication Required** (must be comment owner or staff)

#### Like Comment
```
POST /api/comments/<comment_id>/like/
```
**Authentication Required**

Returns the created like object.

#### Unlike Comment
```
DELETE /api/comments/<comment_id>/unlike/
```
**Authentication Required**

#### Get Comment Replies
```
GET /api/comments/<comment_id>/replies/
```
Returns all replies to a specific comment.

### Comment Likes

#### List Likes
```
GET /api/comment-likes/
```
Returns all comment likes.

#### Get Single Like
```
GET /api/comment-likes/<like_id>/
```

## Response Examples

### Comment Object
```json
{
  "comment_id": "123e4567-e89b-12d3-a456-426614174000",
  "user": "user-uuid",
  "user_username": "john_doe",
  "text": "This is a great chapter!",
  "content_type_display": "chapter",
  "parent_comment": null,
  "like_count": 5,
  "reply_count": 2,
  "is_liked_by_user": true,
  "replies": [
    {
      "comment_id": "456e7890-e89b-12d3-a456-426614174001",
      "user": "another-user-uuid",
      "user_username": "jane_smith",
      "text": "I agree!",
      "parent_comment": "123e4567-e89b-12d3-a456-426614174000",
      "like_count": 1,
      "is_liked_by_user": false,
      "created_at": "2023-11-09T19:00:00Z",
      "updated_at": "2023-11-09T19:00:00Z"
    }
  ],
  "created_at": "2023-11-09T18:30:00Z",
  "updated_at": "2023-11-09T18:30:00Z"
}
```

## Usage Examples

### Comment on a Series
```bash
curl -X POST http://localhost:8000/api/comments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Amazing story!",
    "content_type": "series",
    "object_id": "series-uuid"
  }'
```

### Reply to a Comment
```bash
curl -X POST http://localhost:8000/api/comments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Thanks for reading!",
    "parent_comment": "parent-comment-uuid"
  }'
```

### Like a Comment
```bash
curl -X POST http://localhost:8000/api/comments/<comment-id>/like/ \
  -H "Authorization: Bearer <token>"
```

### Get Comments for a Chapter
```bash
curl http://localhost:8000/api/comments/by_content/?content_type=chapter&object_id=<chapter-uuid>
```

## Permissions

- **Read**: Anyone can view comments (including anonymous users)
- **Create**: Authenticated users only
- **Update**: Only the comment owner can edit their comment
- **Delete**: Only the comment owner or staff can delete a comment
- **Like/Unlike**: Authenticated users only

## Admin Interface

Both Comment and CommentLike models are registered in the Django admin interface with:
- Search and filter capabilities
- Read-only fields for IDs and timestamps
- Calculated fields (like_count, reply_count)
