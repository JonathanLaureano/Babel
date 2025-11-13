"""
"""Translation service module using Google Gemini API.
Adapted from Rosetta project for Django integration.
"""
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async
import logging
from .models import TranslationJob, TranslatedChapterCache
from .scraper import scrape_novel_page, get_chapter_pages, scrape_chapter_page

logger = logging.getLogger(__name__)

# System instruction for the initial translation
TRANSLATOR_SYSTEM_PROMPT = """
You are an expert translator specializing in Korean to English translation, 
with a deep understanding of fictional novels. Your task is to translate the
following Korean text into English. 

Focus on:
1.  **Accuracy:** Faithfully convey the original meaning.
2.  **Tone:** Preserve the original author's tone and style (e.g., formal,
    informal, suspenseful, humorous).
3.  **Nuance:** Capture subtle meanings, cultural references, and wordplay
    where possible.

Provide only the translated English text, with no additional commentary.
"""

# System instruction for translating metadata (titles, descriptions, etc.)
METADATA_TRANSLATOR_PROMPT = """
You are an expert translator specializing in Korean to English translation.
Translate the following text accurately and naturally into English.

Provide only the translated text, with no additional commentary or explanation.
"""

# System instruction for the editing pass
EDITOR_SYSTEM_PROMPT = """
You are a senior fictional novel editor at a major publishing house. You have
been handed a raw, literal translation of a Korean novel chapter. 

Your task is to **polish this raw translation** into natural, flowing, and
publishable English. 

Focus on:
1.  **Flow and Readability:** Make it read like it was originally written
    in English.
2.  **Grammar and Syntax:** Correct any awkward phrasing, grammatical errors,
    or unnatural sentence structures.
3.  **Diction:** Choose words that are evocative and appropriate for a
    fictional novel.
4.  **Consistency:** Ensure the tone and character voices are consistent.

**Important:** Do not change the core meaning, plot points, or character
details from the original translation. Your job is to elevate the language,
not to rewrite the story.

Provide only the final, polished English text.
"""


def configure_gemini():
    """Configure Gemini API with key from settings."""
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in settings")
    genai.configure(api_key=api_key)


def call_gemini(system_prompt: str, user_text: str, prompt_dictionary: dict = None) -> str:
    """
    Calls the Gemini API with a system prompt and user text.
    
    Args:
        system_prompt: System instruction for the model
        user_text: User text to process
        prompt_dictionary: Optional dictionary of terms for consistent translation
        
    Returns:
        Generated text response
        
    Raises:
        Exception: If API call fails
    """
    try:
        # If prompt dictionary exists, augment the user text with translation guidelines
        if prompt_dictionary:
            dictionary_str = "\n\n**Translation Dictionary (use these translations consistently):**\n"
            for key, value in prompt_dictionary.items():
                dictionary_str += f"- {key}: {value}\n"
            user_text = dictionary_str + "\n" + user_text
        
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')
        model = genai.GenerativeModel(
            model_name,
            system_instruction=system_prompt
        )
        response = model.generate_content(user_text)
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise


def translate_text(text: str, prompt_type: str = 'content') -> str:
    """
    Translate Korean text to English using appropriate prompt.
    
    Args:
        text: Korean text to translate
        prompt_type: 'content' or 'metadata'
        
    Returns:
        Translated English text
    """
    configure_gemini()
    prompt = METADATA_TRANSLATOR_PROMPT if prompt_type == 'metadata' else TRANSLATOR_SYSTEM_PROMPT
    return call_gemini(prompt, text)


def polish_translation(raw_translation: str) -> str:
    """
    Polish raw translation into natural English.
    
    Args:
        raw_translation: Raw English translation
        
    Returns:
        Polished English text
    """
    configure_gemini()
    return call_gemini(EDITOR_SYSTEM_PROMPT, raw_translation)


def process_novel_metadata(job: TranslationJob) -> bool:
    """
    Scrape and translate novel metadata.
    
    Args:
        job: TranslationJob instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        job.status = 'scraping'
        job.current_operation = 'Scraping novel information'
        job.save()
        
        logger.info(f"Scraping novel page: {job.novel_url}")
        novel_info = scrape_novel_page(job.novel_url)
        
        if not novel_info.get('Title'):
            raise ValueError("Failed to scrape novel information")
        
        # Store Korean metadata
        job.korean_title = novel_info.get('Title')
        job.korean_author = novel_info.get('Author')
        job.korean_genre = novel_info.get('Genre')
        job.korean_description = novel_info.get('Description')
        job.cover_image_url = novel_info.get('Cover_Image')
        job.save()
        
        logger.info(f"Scraped novel: {job.korean_title}")
        
        # Translate metadata
        job.current_operation = 'Translating novel metadata'
        job.save()
        
        configure_gemini()
        
        if job.korean_title:
            logger.info("Translating title...")
            job.english_title = call_gemini(METADATA_TRANSLATOR_PROMPT, job.korean_title)
        
        job.english_author = job.korean_author  # Keep author name as is
        
        if job.korean_genre:
            logger.info("Translating genre...")
            job.english_genre = call_gemini(METADATA_TRANSLATOR_PROMPT, job.korean_genre)
        
        if job.korean_description:
            logger.info("Translating description...")
            job.english_description = call_gemini(METADATA_TRANSLATOR_PROMPT, job.korean_description)
        
        job.save()
        logger.info(f"Translated novel metadata: {job.english_title}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing novel metadata: {e}")
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()
        return False


def process_chapter(job: TranslationJob, chapter_info: dict) -> bool:
    """
    Scrape, translate, and cache a single chapter.
    
    Args:
        job: TranslationJob instance
        chapter_info: Dict with 'number' and 'url'
        
    Returns:
        True if successful, False otherwise
    """
    chapter_num = chapter_info['number']
    chapter_url = chapter_info['url']
    
    try:
        logger.info(f"Processing chapter {chapter_num}")
        
        # Create cache entry with default title
        default_title = f"Chapter {chapter_num}"
        cache, created = TranslatedChapterCache.objects.get_or_create(
            job=job,
            chapter_number=chapter_num,
            defaults={
                'chapter_url': chapter_url,
                'korean_title': default_title,
                'korean_content': '',
                'status': 'pending'
            }
        )
        
        # Step 1: Scrape chapter
        job.current_operation = f'Scraping chapter {chapter_num}'
        job.save()
        
        chapter_data = scrape_chapter_page(chapter_url)
        
        if not chapter_data or not chapter_data.get('Chapter Content'):
            raise ValueError("Failed to scrape chapter content")
        
        # Use scraped title if available, otherwise use default
        scraped_title = chapter_data.get('Chapter Title')
        if scraped_title:
            cache.korean_title = scraped_title
        else:
            # No title found in chapter, use default
            cache.korean_title = default_title
        
        cache.korean_content = chapter_data['Chapter Content']
        cache.status = 'scraped'
        cache.save()
        
        logger.info(f"Scraped chapter {chapter_num}: {cache.korean_title}")
        
        # Step 2: Translate title (or use default if it's "Chapter X")
        job.current_operation = f'Translating chapter {chapter_num} title'
        job.save()
        
        configure_gemini()
        
        # If title is the default "Chapter X", keep it as is in English
        if cache.korean_title == default_title:
            cache.english_title = default_title
            logger.info(f"Using default title: {cache.english_title}")
        else:
            # Translate the Korean title
            cache.english_title = call_gemini(METADATA_TRANSLATOR_PROMPT, cache.korean_title, job.prompt_dictionary)
            logger.info(f"Translated title: {cache.english_title}")
        
        cache.save()
        
        # Step 3: Translate content
        job.current_operation = f'Translating chapter {chapter_num} content'
        job.save()
        
        cache.english_content_raw = call_gemini(TRANSLATOR_SYSTEM_PROMPT, cache.korean_content, job.prompt_dictionary)
        cache.status = 'translated'
        cache.save()
        
        logger.info(f"Translated chapter {chapter_num} content")
        
        # Step 4: Polish
        job.current_operation = f'Polishing chapter {chapter_num}'
        job.save()
        
        cache.english_content_final = call_gemini(EDITOR_SYSTEM_PROMPT, cache.english_content_raw, job.prompt_dictionary)
        cache.status = 'polished'
        cache.save()
        
        logger.info(f"Polished chapter {chapter_num}")
        
        # Update job progress
        job.chapters_completed += 1
        job.save()
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing chapter {chapter_num}: {e}")
        
        # Update cache with error
        try:
            cache = TranslatedChapterCache.objects.get(job=job, chapter_number=chapter_num)
            cache.status = 'failed'
            cache.error_message = str(e)
            cache.save()
        except TranslatedChapterCache.DoesNotExist:
            logger.info(f"Cache entry does not exist for job {job.job_id}, chapter {chapter_num} when marking as failed. This may be expected if the cache was not created yet.")
        
        # Update job
        job.chapters_failed += 1
        job.save()
        
        return False


def start_translation_job(job_id):
    """
    Start processing a translation job.
    
    Args:
        job_id: UUID of the TranslationJob
        
    This function should be called asynchronously (e.g., via Celery)
    or in a background thread for production use.
    """
    try:
        from library.models import Series, Chapter
        
        job = TranslationJob.objects.get(job_id=job_id)
        
        logger.info(f"Starting translation job {job_id}")
        
        # Process novel metadata
        if not process_novel_metadata(job):
            return
        
        # Check if translate_all flag was set
        translate_all = (job.current_operation == 'translate_all')
        
        # Check if series with same Korean title already exists in library
        start_from_chapter = 1
        existing_series = Series.objects.filter(
            translation_jobs__korean_title=job.korean_title
        ).first()
        
        if existing_series:
            logger.info(f"Found existing series: {existing_series.title} ({existing_series.series_id})")
            
            # Find the highest chapter number already translated
            highest_chapter = Chapter.objects.filter(
                series=existing_series
            ).order_by('-chapter_number').first()
            
            if highest_chapter:
                start_from_chapter = highest_chapter.chapter_number + 1
                logger.info(f"Highest chapter found: {highest_chapter.chapter_number}. Starting from chapter {start_from_chapter}")
            else:
                logger.info("No chapters found in existing series. Starting from chapter 1")
        else:
            logger.info("No existing series found. Starting from chapter 1")
        
        # Get chapter list starting from determined chapter
        job.status = 'translating'
        job.current_operation = f'Getting chapter list (starting from {start_from_chapter})'
        job.save()
        
        # Get all available chapters from the website starting from start_from_chapter
        all_available_chapters = get_chapter_pages(
            job.novel_url,
            limit=10000,  # Get all available chapters
            start_from=start_from_chapter
        )
        
        if not all_available_chapters:
            # No new chapters available
            if existing_series:
                error_msg = f"All chapters already translated. Latest chapter: {start_from_chapter - 1}"
                logger.info(error_msg)
                job.status = 'failed'
                job.error_message = error_msg
                job.completed_at = timezone.now()
                job.save()
                return
            else:
                raise ValueError("Failed to get chapter list")
        
        # Determine how many chapters to process
        if translate_all:
            # Translate all available chapters
            chapters = all_available_chapters
            job.chapters_requested = len(chapters)
            job.save()
            logger.info(f"Translate all mode: Processing all {len(chapters)} available chapters")
        else:
            # Limit to requested number of chapters
            chapters = all_available_chapters[:job.chapters_requested]
        
        logger.info(f"Found {len(all_available_chapters)} available chapters. Processing {len(chapters)} chapters starting from chapter {start_from_chapter}")
        
        # Process each chapter
        for chapter in chapters:
            process_chapter(job, chapter)
        
        # Mark job as completed
        job.status = 'completed'
        job.current_operation = 'Completed'
        job.completed_at = timezone.now()
        job.save()
        
        logger.info(f"Translation job {job_id} completed: {job.chapters_completed}/{job.chapters_requested} chapters")
        
    except TranslationJob.DoesNotExist:
        logger.error(f"Translation job {job_id} not found")
    except Exception as e:
        logger.error(f"Error in translation job {job_id}: {e}")
        try:
            job = TranslationJob.objects.get(job_id=job_id)
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
        except Exception as inner_e:
            logger.error(f"Failed to update job status to 'failed' for job {job_id}: {inner_e}")
