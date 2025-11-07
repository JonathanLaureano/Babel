# Rating and View Tracking Features

This document describes the new rating and view tracking features added to the Babel Library application.

## Overview

Three new features have been added:
1. **Star Ratings** - Users can rate series from 1-5 stars
2. **Author Field** - Series now have an optional author field
3. **View Tracking** - Unique view counts for both Series and Chapters

## Database Models

### SeriesRating
- Stores user ratings for series (1-5 stars)
- One rating per user per series (enforced by unique constraint)
- Ratings cannot be changed (as per requirements)
- Links to both User and Series

### SeriesView
- Tracks unique views for series pages
- Uses visitor_id to identify unique visitors
- For authenticated users: `user_{user_id}`
- For anonymous users: session key or IP address

### ChapterView
- Tracks unique views for chapter pages
- Uses same visitor_id system as SeriesView
- Chapter views contribute to parent series total view count

## API Endpoints

### Rate a Series
**POST** `/api/series/{series_id}/rate/`

Rate a series from 1-5 stars. Requires authentication.

**Request Body:**
```json
{
  "rating": 5
}
```

**Response (201 Created):**
```json
{
  "rating_id": "uuid",
  "series": "series_uuid",
  "user": "user_uuid",
  "user_username": "john_doe",
  "rating": 5,
  "created_at": "2025-11-07T15:00:00Z",
  "updated_at": "2025-11-07T15:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Not authenticated
- `400 Bad Request` - Invalid rating value or already rated

### Track Series View
**POST** `/api/series/{series_id}/track_view/`

Track a view for a series. Works for both authenticated and anonymous users.

**Response (200 OK):**
```json
{
  "message": "View tracked",
  "view_count": 42
}
```

### Track Chapter View
**POST** `/api/chapters/{chapter_id}/track_view/`

Track a view for a chapter. Works for both authenticated and anonymous users.

**Response (200 OK):**
```json
{
  "message": "View tracked",
  "view_count": 15
}
```

## Serializer Changes

### SeriesSerializer
New read-only fields:
- `author` (string, nullable) - Author of the series
- `average_rating` (float) - Average rating from all user ratings (0 if no ratings)
- `total_view_count` (integer) - Unique visitors who viewed the series or any of its chapters

### ChapterSerializer
New read-only field:
- `view_count` (integer) - Unique visitors who viewed this chapter

## View Count Logic

### Series View Count
A series' `total_view_count` includes:
1. Direct series page views
2. Unique visitors from all chapter views

The count eliminates duplicates - if a visitor views both the series page and a chapter, they count as one unique view.

### Chapter View Count
A chapter's `view_count` is simply the number of unique visitors who viewed that chapter.

## Visitor Identification

The system identifies unique visitors using:
1. **Authenticated users**: `user_{user_id}`
2. **Anonymous users**: Django session key (created if needed) or IP address as fallback

This ensures:
- Each visitor is counted only once per series/chapter
- Both logged-in and anonymous users are tracked
- Users are tracked consistently across sessions (if logged in)

## Admin Panel

All new models are registered in the Django admin panel:
- `SeriesRating` - View and manage user ratings
- `SeriesView` - View series view tracking data
- `ChapterView` - View chapter view tracking data

The `Series` and `Chapter` admin pages now display the computed `average_rating` and `view_count` fields.

## Testing

To test the features:

1. **Rate a series** (requires authentication):
```bash
curl -X POST http://localhost:8000/api/series/{series_id}/rate/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5}'
```

2. **Track a series view**:
```bash
curl -X POST http://localhost:8000/api/series/{series_id}/track_view/ \
  -H "Content-Type: application/json"
```

3. **Track a chapter view**:
```bash
curl -X POST http://localhost:8000/api/chapters/{chapter_id}/track_view/ \
  -H "Content-Type: application/json"
```

4. **Get series details** (includes new fields):
```bash
curl http://localhost:8000/api/series/{series_id}/
```

## Notes

- Ratings are immutable - users cannot change their rating once submitted
- View tracking uses database-level unique constraints to prevent duplicate counting
- The `average_rating` and `total_view_count` are computed properties, not stored fields
- View tracking automatically handles session creation for anonymous users
