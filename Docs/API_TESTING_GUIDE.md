# API Testing Guide - Prompt Dictionary

## Prerequisites

1. Start the Django backend server:
```bash
cd Backend/babelLibrary
source ../venv/bin/activate
python manage.py runserver
```

2. Get an authentication token (if required) or create a superuser:
```bash
python manage.py createsuperuser
```

## Testing with curl

### 1. Create a Translation Job with Prompt Dictionary

```bash
curl -X POST http://localhost:8000/api/translator/jobs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -d '{
    "novel_url": "https://novel-site.com/test-novel",
    "chapters_requested": 5,
    "prompt_dictionary": {
      "김민준": "Kim Min-jun",
      "불사 연맹": "Immortal Alliance",
      "천계": "Celestial Realm",
      "마나": "Mana"
    }
  }' | python -m json.tool
```

Expected response:
```json
{
  "job_id": "uuid-here",
  "novel_url": "https://novel-site.com/test-novel",
  "status": "pending",
  "prompt_dictionary": {
    "김민준": "Kim Min-jun",
    "불사 연맹": "Immortal Alliance",
    "천계": "Celestial Realm",
    "마나": "Mana"
  },
  "chapters_requested": 5,
  "chapters_completed": 0,
  ...
}
```

### 2. Get Translation Job Details

```bash
curl http://localhost:8000/api/translator/jobs/{JOB_ID}/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" | python -m json.tool
```

Verify that the `prompt_dictionary` field is present in the response.

### 3. Get Series with Prompt Dictionary

After importing a job to the library:

```bash
curl http://localhost:8000/api/library/series/{SERIES_ID}/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" | python -m json.tool
```

Expected response includes:
```json
{
  "series_id": "uuid-here",
  "title": "Test Novel",
  "author": "Test Author",
  "prompt_dictionary": {
    "김민준": "Kim Min-jun",
    "불사 연맹": "Immortal Alliance",
    ...
  },
  ...
}
```

### 4. List All Translation Jobs

```bash
curl http://localhost:8000/api/translator/jobs/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" | python -m json.tool
```

### 5. Import Job to Library

```bash
curl -X POST http://localhost:8000/api/translator/jobs/{JOB_ID}/import_to_library/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -d '{
    "status": "Ongoing"
  }' | python -m json.tool
```

The prompt_dictionary will automatically transfer from the job to the created series.

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = "your_auth_token_here"
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Create a job with prompt dictionary
job_data = {
    "novel_url": "https://novel-site.com/test",
    "chapters_requested": 5,
    "prompt_dictionary": {
        "김민준": "Kim Min-jun",
        "불사 연맹": "Immortal Alliance",
        "천계": "Celestial Realm"
    }
}

response = requests.post(
    f"{BASE_URL}/translator/jobs/",
    json=job_data,
    headers=headers
)

job = response.json()
print(f"Job created: {job['job_id']}")
print(f"Dictionary: {job['prompt_dictionary']}")

# Get job details
job_id = job['job_id']
response = requests.get(
    f"{BASE_URL}/translator/jobs/{job_id}/",
    headers=headers
)

job_details = response.json()
print(f"Retrieved dictionary: {job_details['prompt_dictionary']}")
```

## Verification Checklist

- [ ] Migrations applied successfully
- [ ] Test script passes all tests
- [ ] Can create translation job with prompt_dictionary via API
- [ ] Can retrieve job and see prompt_dictionary in response
- [ ] Dictionary transfers to Series on import
- [ ] Can retrieve Series and see prompt_dictionary
- [ ] Frontend TypeScript interfaces match backend structure
- [ ] Dictionary is used during actual translation (check logs)

## Troubleshooting

**Issue**: `prompt_dictionary` not in API response
- Check migrations are applied: `python manage.py showmigrations`
- Verify serializers include the field
- Restart Django server

**Issue**: Translation doesn't use dictionary terms
- Check translator_service.py `call_gemini()` function
- Verify dictionary is being passed to the function
- Check logs for dictionary usage

**Issue**: Dictionary not transferring to Series
- Verify views.py import function includes prompt_dictionary
- Check if job.prompt_dictionary is not None before import

## Next: Frontend Integration

Once API testing is complete:
1. Create UI form for entering dictionary entries
2. Display dictionary in job/series details pages
3. Add validation for dictionary format
4. Implement dictionary editing functionality
