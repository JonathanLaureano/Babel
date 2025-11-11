# Prompt Dictionary Feature

## Overview

The **Prompt Dictionary** feature ensures consistent translation of character names, organizations, and recurring terms throughout a series. This is especially important for maintaining consistency across multiple chapters and translation sessions.

## How It Works

When creating a translation job, you can provide a dictionary of terms that should be translated consistently:

```json
{
  "novel_url": "https://example.com/novel",
  "chapters_requested": 10,
  "prompt_dictionary": {
    "김민준": "Kim Min-jun",
    "불사 연맹": "Immortal Alliance",
    "천계": "Celestial Realm",
    "마나": "Mana"
  }
}
```

### Backend Implementation

1. **Models**: Both `TranslationJob` and `Series` models have a `prompt_dictionary` JSONField
2. **Translation Service**: The dictionary is automatically included in all translation prompts
3. **Import**: When a job is imported to the library, the prompt dictionary is transferred to the Series

### Frontend Implementation

The prompt dictionary is available in:
- `TranslationJob` interface
- `CreateTranslationJobRequest` interface
- `Series` interface

## Usage Example

### Creating a Translation Job with Prompt Dictionary

```typescript
const request: CreateTranslationJobRequest = {
  novel_url: 'https://novel-site.com/my-novel',
  chapters_requested: 5,
  prompt_dictionary: {
    '김민준': 'Kim Min-jun',
    '불사 연맹': 'Immortal Alliance',
    '천계': 'Celestial Realm'
  }
};

translatorService.createJob(request).subscribe(job => {
  console.log('Job created with prompt dictionary:', job.prompt_dictionary);
});
```

### Viewing Series Prompt Dictionary

```typescript
libraryService.getSeries(seriesId).subscribe(series => {
  if (series.prompt_dictionary) {
    console.log('Translation dictionary:', series.prompt_dictionary);
    // Display in UI to show how terms were translated
  }
});
```

## API Endpoints

### Create Translation Job
```
POST /api/translator/jobs/
```

Request body:
```json
{
  "novel_url": "https://...",
  "chapters_requested": 10,
  "prompt_dictionary": {
    "korean_term_1": "English Translation 1",
    "korean_term_2": "English Translation 2"
  }
}
```

### Get Translation Job
```
GET /api/translator/jobs/{job_id}/
```

Response includes `prompt_dictionary` field.

### Get Series
```
GET /api/library/series/{series_id}/
```

Response includes `prompt_dictionary` field inherited from the translation job.

## Database Migrations

Two migrations were created:
1. `library/migrations/0003_series_prompt_dictionary.py` - Adds prompt_dictionary to Series
2. `translator/migrations/0003_translationjob_prompt_dictionary.py` - Adds prompt_dictionary to TranslationJob

To apply migrations:
```bash
cd Backend/babelLibrary
source ../venv/bin/activate
python manage.py migrate
```

## Benefits

1. **Consistency**: Character names and terms are translated the same way every time
2. **Quality**: Reduces confusion and improves readability
3. **Flexibility**: Users can define their own preferred translations
4. **Persistence**: Dictionary is saved with the series for future reference
5. **Continuity**: When translating additional chapters for an existing series, the same dictionary can be reused

## Best Practices

1. **Character Names**: Include all main character names with your preferred romanization
2. **Organizations**: Add guild names, factions, and other groups
3. **Special Terms**: Include magic systems, cultivation terms, or unique concepts
4. **Locations**: Add important place names for consistency
5. **Titles**: Include character titles and ranks

Example comprehensive dictionary:
```json
{
  "김민준": "Kim Min-jun",
  "불사 연맹": "Immortal Alliance",
  "천계": "Celestial Realm",
  "마나": "Mana",
  "검황": "Sword Emperor",
  "천산": "Heaven Mountain",
  "무림": "Murim"
}
```

## Future Enhancements

Potential improvements:
- Auto-suggest dictionary entries based on frequently occurring terms
- Import dictionary from previous series by the same author
- Share dictionaries across similar series
- Validate dictionary entries against translation output
