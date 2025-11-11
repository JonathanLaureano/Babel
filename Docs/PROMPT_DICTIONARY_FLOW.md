# Prompt Dictionary - System Flow

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER CREATES JOB                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │   POST /api/translator/jobs/                 │
        │                                              │
        │   {                                          │
        │     "novel_url": "...",                      │
        │     "chapters_requested": 10,                │
        │     "prompt_dictionary": {                   │
        │       "김민준": "Kim Min-jun",                │
        │       "불사 연맹": "Immortal Alliance"         │
        │     }                                        │
        │   }                                          │
        └──────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │      TranslationJob Created in Database      │
        │                                              │
        │   ✅ job.prompt_dictionary stored            │
        │   ✅ Background thread starts translation    │
        └──────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSLATION PROCESS                          │
└─────────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────┐            ┌─────────┐              ┌─────────┐
│ Title   │            │ Content │              │ Polish  │
│ Trans.  │            │ Trans.  │              │ Trans.  │
└─────────┘            └─────────┘              └─────────┘
    │                         │                         │
    │  call_gemini()         │  call_gemini()          │  call_gemini()
    │  + dictionary          │  + dictionary           │  + dictionary
    │                         │                         │
    └─────────────────────────┴─────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │     Dictionary Prepended to Each Prompt      │
        │                                              │
        │ "**Translation Dictionary:**                │
        │  - 김민준: Kim Min-jun                       │
        │  - 불사 연맹: Immortal Alliance              │
        │                                              │
        │ [Korean content to translate...]"           │
        └──────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │    Gemini AI Uses Dictionary for Context    │
        │                                              │
        │   ✅ Consistent character names              │
        │   ✅ Consistent organization names           │
        │   ✅ Consistent special terms                │
        └──────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │   TranslatedChapterCache (per chapter)       │
        │                                              │
        │   ✅ english_title                           │
        │   ✅ english_content_raw                     │
        │   ✅ english_content_final                   │
        └──────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       JOB COMPLETE                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │   POST /api/translator/jobs/{id}/            │
        │        import_to_library/                    │
        │                                              │
        │   {                                          │
        │     "status": "Ongoing"                      │
        │   }                                          │
        └──────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │         Series Created in Library            │
        │                                              │
        │   series.prompt_dictionary = job.prompt_dictionary
        │   ✅ Dictionary transferred automatically    │
        │   ✅ Linked to job via imported_series       │
        └──────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────────┐
        │   Chapters Created in Library                │
        │                                              │
        │   ✅ chapter.content from cache              │
        │   ✅ Linked to series                        │
        └──────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AVAILABLE IN LIBRARY                          │
└─────────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────┐            ┌─────────┐              ┌─────────┐
│  Users  │            │  API    │              │ Future  │
│  Read   │            │ Access  │              │  Ref.   │
│ Series  │            │ Dict.   │              │         │
└─────────┘            └─────────┘              └─────────┘
```

## Database Schema

```
TranslationJob
├── job_id (UUID, PK)
├── novel_url
├── korean_title
├── english_title
├── prompt_dictionary (JSONField) ◄─┐
├── chapters_requested                │
├── chapters_completed                │
├── status                            │
└── imported_series (FK to Series)    │
                                      │
                                      │ Transfers on import
                                      │
Series                                │
├── series_id (UUID, PK)              │
├── title                             │
├── author                            │
├── description                       │
├── prompt_dictionary (JSONField) ◄───┘
├── status
└── created_at
```

## Code Path

### 1. Job Creation
```python
# translator/views.py
def create(self, request):
    serializer = CreateTranslationJobSerializer(data=request.data)
    job = serializer.save()  # prompt_dictionary stored
    start_translation_job(job.job_id)
```

### 2. Translation
```python
# translator/translator_service.py
def call_gemini(system_prompt, user_text, prompt_dictionary=None):
    if prompt_dictionary:
        dictionary_str = "\n**Translation Dictionary:**\n"
        for key, value in prompt_dictionary.items():
            dictionary_str += f"- {key}: {value}\n"
        user_text = dictionary_str + "\n" + user_text
    
    # Send to Gemini API with dictionary context
```

### 3. Import to Library
```python
# translator/views.py
def import_to_library(self, request, job_id=None):
    series = Series.objects.create(
        title=job.english_title,
        author=job.english_author,
        prompt_dictionary=job.prompt_dictionary  # Transfer
    )
```

## Frontend Integration

```typescript
// models/translator.ts
export interface CreateTranslationJobRequest {
  novel_url: string;
  chapters_requested?: number;
  prompt_dictionary?: Record<string, string>;
}

// Component usage
const job = {
  novel_url: 'https://...',
  chapters_requested: 10,
  prompt_dictionary: {
    '김민준': 'Kim Min-jun',
    '불사 연맹': 'Immortal Alliance'
  }
};

this.translatorService.createJob(job).subscribe(...);
```

## Benefits at Each Stage

1. **Job Creation**: User defines consistency rules upfront
2. **Translation**: AI respects user preferences automatically
3. **Polishing**: Maintains consistency through refinement
4. **Import**: Dictionary preserved for reference
5. **Reading**: Consistent terminology enhances reader experience
6. **Future**: Can reuse dictionary for additional chapters

## Example Consistency

Without dictionary:
```
Chapter 1: "Kim Minjun entered the Undying Alliance's headquarters..."
Chapter 2: "Kim Min-jun walked into the Immortal Alliance building..."
Chapter 3: "Min-jun arrived at the Deathless Federation..."
```

With dictionary:
```
Chapter 1: "Kim Min-jun entered the Immortal Alliance's headquarters..."
Chapter 2: "Kim Min-jun walked into the Immortal Alliance building..."
Chapter 3: "Kim Min-jun arrived at the Immortal Alliance..."
```

✅ **Consistent naming across all chapters!**
