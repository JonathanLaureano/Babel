# Translator App - Quick Start Guide

## Setup (5 minutes)

### 1. Get Gemini API Key
1. Go to https://aistudio.google.com
2. Sign in with Google
3. Click "Get API key"
4. Copy your API key

### 2. Add to Environment
Edit your `.env` file:
```bash
GEMINI_API_KEY=paste_your_key_here
```

### 3. Verify Installation
```bash
# Check migrations are applied
python manage.py showmigrations translator

# Should show:
# translator
#  [X] 0001_initial

# Check for errors
python manage.py check

# Should show: "System check identified no issues (0 silenced)."
```

## Test the API (10 minutes)

### 1. Start Server
```bash
python manage.py runserver
```

### 2. Get Authentication Token
You need an admin user token. If you don't have one:
```bash
python manage.py createsuperuser
```

Then login via API:
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

Save the `access` token from response.

### 3. Create Test Translation Job

**Important:** Start with just 1-2 chapters for testing!

```bash
curl -X POST http://localhost:8000/api/translator/jobs/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "novel_url": "https://booktoki.com/novel/4007556",
    "chapters_requested": 1
  }'
```

Copy the `job_id` from response.

### 4. Check Progress
```bash
curl http://localhost:8000/api/translator/jobs/JOB_ID/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Keep checking every few seconds. Watch the `progress_percentage` field.

### 5. Preview Results
Once `status` is `completed`:
```bash
curl http://localhost:8000/api/translator/jobs/JOB_ID/preview/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Import to Library
```bash
curl -X POST http://localhost:8000/api/translator/jobs/JOB_ID/import_to_library/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Ongoing"
  }'
```

### 7. Verify Import
Check the library:
```bash
curl http://localhost:8000/api/library/series/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

You should see your newly imported novel!

## Using Django Admin

1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Navigate to:
   - **Translator > Translation jobs** - See all jobs
   - **Translator > Translated chapter caches** - See cached chapters
   - **Library > Series** - See imported novels

## Troubleshooting

### Job stuck at "pending"
- Check server logs for errors
- Verify Gemini API key is correct
- Make sure background thread started (check console output)

### "ModuleNotFoundError: No module named 'google'"
```bash
pip install google-generativeai requests beautifulsoup4
```

### "GEMINI_API_KEY not found in settings"
- Check `.env` file has the key
- Restart Django server after adding key

### Scraping fails
- Verify the novel URL is accessible in browser
- Check if website structure matches scraper expectations
- Try a different novel from the same site

### Translation fails
- Check Gemini API quota/limits
- Try with shorter content (1 chapter)
- Verify API key has proper permissions

## API Endpoints Reference

### Base URL
```
http://localhost:8000/api/translator/
```

### Endpoints
```
POST   /jobs/                      Create job
GET    /jobs/                      List all jobs
GET    /jobs/{id}/                 Get job details
GET    /jobs/{id}/preview/         Preview translation
GET    /jobs/{id}/chapters/        Get all chapters
POST   /jobs/{id}/import_to_library/  Import to library
DELETE /jobs/{id}/                 Delete job
```

## Next Steps

1. **Test with 1 chapter** - Make sure it works end-to-end
2. **Try 5 chapters** - Test with more content
3. **Check translation quality** - Review the polished English
4. **Import to library** - Verify Series and Chapters created
5. **Build frontend UI** - Integrate with your Angular admin panel

## Tips

- **Start small**: Always test with 1-2 chapters first
- **Monitor progress**: The translation process takes time (1-2 minutes per chapter)
- **Check logs**: Django logs show detailed progress
- **Preview first**: Always preview before importing
- **API rate limits**: Be mindful of Gemini API quotas

## Need Help?

1. Check `translator/README.md` for full documentation
2. Review `TRANSLATOR_IMPLEMENTATION.md` for architecture details
3. Check Django logs for detailed error messages
4. Verify all prerequisites are installed

## Success Checklist

- [ ] Gemini API key added to `.env`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Server runs without errors
- [ ] Can create translation job via API
- [ ] Job completes successfully
- [ ] Can preview translated content
- [ ] Can import to library
- [ ] Series and chapters appear in library API

Once all items are checked, you're ready to build the frontend! 🎉
