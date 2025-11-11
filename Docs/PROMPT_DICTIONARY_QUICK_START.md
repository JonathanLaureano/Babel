# Prompt Dictionary Quick Start Guide

## What is it?
A feature that ensures character names, organizations, and special terms are translated consistently across all chapters of a series.

## Setup (One-time)

Apply database migrations:
```bash
cd Backend/babelLibrary
source ../venv/bin/activate
python manage.py migrate
```

## Usage

### Example 1: Create a Translation Job with Dictionary

**Request:**
```bash
curl -X POST http://localhost:8000/api/translator/jobs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "novel_url": "https://novel-site.com/my-novel",
    "chapters_requested": 10,
    "prompt_dictionary": {
      "김민준": "Kim Min-jun",
      "불사 연맹": "Immortal Alliance",
      "천계": "Celestial Realm",
      "마나": "Mana"
    }
  }'
```

**TypeScript:**
```typescript
const request: CreateTranslationJobRequest = {
  novel_url: 'https://novel-site.com/my-novel',
  chapters_requested: 10,
  prompt_dictionary: {
    '김민준': 'Kim Min-jun',
    '불사 연맹': 'Immortal Alliance',
    '천계': 'Celestial Realm',
    '마나': 'Mana'
  }
};

this.translatorService.createJob(request).subscribe(
  job => console.log('Job created:', job.job_id),
  error => console.error('Error:', error)
);
```

### Example 2: View Translation Dictionary

**Get Job Dictionary:**
```bash
curl http://localhost:8000/api/translator/jobs/{job_id}/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Series Dictionary:**
```bash
curl http://localhost:8000/api/library/series/{series_id}/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Dictionary Entries

### Character Names
```json
{
  "김민준": "Kim Min-jun",
  "이서연": "Lee Seo-yeon",
  "박지후": "Park Ji-hoo"
}
```

### Organizations
```json
{
  "무림맹": "Murim Alliance",
  "마교": "Demonic Cult",
  "천마교": "Heavenly Demon Sect"
}
```

### Cultivation/Ranks
```json
{
  "검황": "Sword Emperor",
  "마황": "Demon Emperor",
  "천마": "Heavenly Demon"
}
```

### Locations
```json
{
  "천산": "Heaven Mountain",
  "마계": "Demon Realm",
  "중원": "Central Plains"
}
```

### Complete Example
```json
{
  "prompt_dictionary": {
    "김민준": "Kim Min-jun",
    "무림맹": "Murim Alliance",
    "검황": "Sword Emperor",
    "천산": "Heaven Mountain",
    "마나": "Mana",
    "천계": "Celestial Realm"
  }
}
```

## Tips

1. **Start Simple**: Include only the most important recurring terms
2. **Be Consistent**: Use the same romanization style (e.g., "Min-jun" vs "Minjun")
3. **Update as Needed**: Add new terms as they appear in later chapters
4. **Save Templates**: Keep common dictionaries for reuse across similar series

## Troubleshooting

**Problem**: Terms not being translated consistently
- Ensure the dictionary is included in the job creation request
- Check that the Korean terms match exactly (including spaces and punctuation)

**Problem**: Dictionary not appearing in Series
- Verify the job was imported successfully
- Check that the job had a dictionary when it was created

**Problem**: Migration errors
- Make sure virtual environment is activated
- Run `python manage.py migrate` again
- Check database connection

## Next Steps

After setting up your first translation with a prompt dictionary:
1. Monitor the translation progress
2. Review the first translated chapter to verify terms are used correctly
3. Import to library once satisfied
4. Use the same dictionary for future chapters in the series
