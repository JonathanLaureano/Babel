# Translator App - Korean Novel Translation System

A Django app that scrapes, translates, and imports Korean web novels into the Babel library using Google Gemini API.

## Overview

This app is adapted from the Rosetta project and provides:
- Web scraping of Korean novel websites
- Two-step translation (Expert Translator → Novel Editor)
- Translation job tracking and progress monitoring
- Preview before importing to library
- Admin approval workflow for frontend integration

## Features

- **Web Scraping**: Extracts novel metadata and chapter content from Korean websites
- **Translation Pipeline**: 
  1. Scrape Korean content
  2. Translate title and content
  3. Polish translation for natural English
- **Job Management**: Track translation progress with status updates
- **Preview System**: Review translations before importing
- **Selective Import**: Choose which chapters to import
- **Admin Interface**: Django admin integration for management

## API Endpoints

All endpoints require authentication (admin users only).

### Base URL
```
/api/translator/
```

### Available Endpoints

#### 1. Create Translation Job
```http
POST /api/translator/jobs/
```

**Request Body:**
```json
{
  "novel_url": "https://example.com/novel/12345",
  "chapters_requested": 5
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "novel_url": "https://...",
  "status": "pending",
  "chapters_requested": 5,
  "chapters_completed": 0,
  "chapters_failed": 0,
  "progress_percentage": 0,
  "current_operation": null,
  "created_at": "2025-11-10T19:00:00Z"
}
```

#### 2. List All Jobs
```http
GET /api/translator/jobs/
```

**Response:** Array of translation jobs (simplified view)

#### 3. Get Job Details
```http
GET /api/translator/jobs/{job_id}/
```

**Response:** Full job details including all cached chapters

#### 4. Preview Translation
```http
GET /api/translator/jobs/{job_id}/preview/
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "english_title": "Novel Title",
  "english_author": "Author Name",
  "english_genre": "Fantasy",
  "english_description": "Description...",
  "chapters_requested": 5,
  "chapters_completed": 5,
  "chapters": [
    {
      "cache_id": "uuid",
      "chapter_number": 1,
      "english_title": "Chapter 1: Beginning",
      "word_count": 3500,
      "status": "polished"
    }
  ]
}
```

#### 5. Get Chapter Details
```http
GET /api/translator/jobs/{job_id}/chapters/
```

**Response:** Array of all cached chapters with full content (Korean + English)

#### 6. Import to Library
```http
POST /api/translator/jobs/{job_id}/import_to_library/
```

**Request Body:**
```json
{
  "cover_image_url": "https://example.com/cover.jpg",
  "status": "Ongoing",
  "selected_chapters": [1, 2, 3]
}
```

**Note:** `selected_chapters` is optional. If not provided, all polished chapters will be imported.

**Response:**
```json
{
  "message": "Successfully imported to library",
  "series_id": "uuid",
  "series_title": "Novel Title",
  "chapters_imported": 3
}
```

#### 7. Delete Job
```http
DELETE /api/translator/jobs/{job_id}/
```

**Note:** Can only delete jobs that haven't been imported yet.

## Models

### TranslationJob
Tracks the translation job from start to finish.

**Fields:**
- `job_id`: UUID primary key
- `novel_url`: URL of the novel to translate
- `status`: pending | scraping | translating | completed | failed
- Korean metadata: title, author, genre, description
- English metadata: title, author, genre, description
- Progress tracking: chapters_requested, chapters_completed, chapters_failed
- Timestamps: created_at, updated_at, completed_at
- `imported_series`: Link to created Series (after import)

### TranslatedChapterCache
Stores translated chapter content before import.

**Fields:**
- `cache_id`: UUID primary key
- `job`: Foreign key to TranslationJob
- `chapter_number`: Chapter number
- `chapter_url`: Original URL
- Korean content: title, content
- English content: title, content_raw, content_final
- `word_count`: Calculated from final content
- `status`: pending | scraped | translated | polished | failed
- `imported_chapter`: Link to created Chapter (after import)

## Translation Pipeline

1. **Scrape Novel Info**
   - Extract title, author, genre, description
   - Translate all metadata to English

2. **Get Chapter List**
   - Extract chapter URLs from novel page
   - Start from chapter 1 (not reverse order)

3. **Process Each Chapter**
   - Scrape: Get Korean title and content
   - Translate Title: Use metadata translator prompt
   - Translate Content: Use expert translator prompt
   - Polish: Use novel editor prompt for natural English

4. **Cache Results**
   - Store in TranslatedChapterCache
   - Track status at each step
   - Calculate word count

5. **Preview & Approve**
   - Frontend reviews translated content
   - Admin can edit if needed
   - Select which chapters to import

6. **Import to Library**
   - Create Series with English metadata
   - Create Chapters with polished content
   - Link Genre (create if doesn't exist)
   - Mark job as imported

## Configuration

### Environment Variables

Add to `.env`:
```bash
GEMINI_API_KEY=your_google_gemini_api_key
```

### Settings

In `settings.py`:
```python
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
GEMINI_MODEL = 'gemini-2.0-flash-exp'  # Default model
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Sign in with Google account
3. Click "Get API key"
4. Create new API key
5. Add to `.env` file

## Usage Examples

### Python/JavaScript Frontend

```javascript
// Create translation job
const response = await fetch('/api/translator/jobs/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    novel_url: 'https://example.com/novel/123',
    chapters_requested: 5
  })
});
const job = await response.json();

// Poll for status
const checkStatus = async (jobId) => {
  const res = await fetch(`/api/translator/jobs/${jobId}/`);
  const data = await res.json();
  return data;
};

// Preview when completed
const preview = await fetch(`/api/translator/jobs/${job.job_id}/preview/`);
const previewData = await preview.json();

// Import to library
await fetch(`/api/translator/jobs/${job.job_id}/import_to_library/`, {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    cover_image_url: 'https://...',
    status: 'Ongoing'
  })
});
```

## Background Processing

Currently, translation jobs run in a background thread. For production:

**Recommended:** Use Celery for proper task queue management.

```python
# Future enhancement - tasks.py
from celery import shared_task
from .translator_service import start_translation_job

@shared_task
def process_translation_job(job_id):
    start_translation_job(job_id)
```

## Admin Interface

Access via Django admin at `/admin/`:

- **Translation Jobs**: View all jobs, status, progress
- **Translated Chapter Cache**: View cached chapters, content

## Error Handling

- **Scraping errors**: Logged and stored in `error_message`
- **Translation errors**: Chapter marked as failed, job continues
- **Import errors**: Rolled back via database transaction

## Limitations

- Web scraping is site-specific (currently optimized for BookToki)
- Translation quality depends on Gemini API
- Long chapters may hit API token limits
- Requires stable internet connection
- Background processing uses threads (use Celery for production)

## Future Enhancements

- [ ] Celery integration for async processing
- [ ] Retry mechanism for failed chapters
- [ ] Support for multiple novel websites
- [ ] Chapter editing before import
- [ ] Batch job management
- [ ] Translation quality metrics
- [ ] Cost tracking for API usage
- [ ] WebSocket for real-time progress updates

## Troubleshooting

### Job stuck in "pending" status
- Check if background thread started successfully
- Verify Gemini API key is valid
- Check logs for errors

### Scraping fails
- Verify novel URL is accessible
- Check if website structure changed
- Update scraper selectors if needed

### Translation fails
- Check Gemini API quota
- Verify API key has proper permissions
- Check content length (may be too long)

### Import fails
- Verify job status is "completed"
- Check that chapters are "polished"
- Ensure no duplicate series exists
- Check database constraints

## Support

For issues or questions:
1. Check Django logs
2. Review job error messages
3. Test scraper with novel URL
4. Verify Gemini API connectivity
