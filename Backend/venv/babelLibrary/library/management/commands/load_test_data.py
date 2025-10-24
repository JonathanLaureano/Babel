from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from library.models import Genre, Series, SeriesGenre, Chapter


class Command(BaseCommand):
    help = 'Load test data into the database based on TestData.sql'

    def handle(self, *args, **options):
        self.stdout.write('Loading test data...')

        # Create genres
        genres_data = [
            'Action', 'Adventure', 'Comedy', 'Detective', 'Drama',
            'Fantasy', 'Mystery', 'Regression', 'Romance', 
            'Slice of Life', 'Thriller'
        ]

        genres = {}
        for genre_name in genres_data:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            genres[genre_name] = genre
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created genre: {genre_name}'))

        # Create series
        series_data = [
            {
                'title': 'The Crimson Blade',
                'description': 'A legendary warrior rises to defend the realm from encroaching darkness.',
                'cover_image_url': 'https://placehold.co/400x600/FF0000/FFFFFF?text=Crimson+Blade',
                'status': 'Ongoing',
                'genres': ['Action', 'Fantasy']
            },
            {
                'title': 'Whispers in the Library',
                'description': 'A young detective unravels ancient secrets hidden within a forgotten library.',
                'cover_image_url': 'https://placehold.co/400x600/000080/FFFFFF?text=Whispers',
                'status': 'Completed',
                'genres': ['Mystery', 'Thriller']
            },
            {
                'title': 'Back to My 18th Life',
                'description': 'After a tragic accident, a salaryman returns to his high school days with future knowledge.',
                'cover_image_url': 'https://placehold.co/400x600/800080/FFFFFF?text=18th+Life',
                'status': 'Ongoing',
                'genres': ['Regression', 'Fantasy']
            },
            {
                'title': 'My Quiet Corner Cafe',
                'description': 'Heartwarming tales of daily life and simple joys at a cozy neighborhood cafe.',
                'cover_image_url': 'https://placehold.co/400x600/008000/FFFFFF?text=Cafe+Life',
                'status': 'Ongoing',
                'genres': ['Slice of Life', 'Romance']
            },
            {
                'title': 'Echoes of the Forgotten Empire',
                'description': 'An adventurer discovers a lost civilization and its powerful, dangerous relics.',
                'cover_image_url': 'https://placehold.co/400x600/800000/FFFFFF?text=Lost+Empire',
                'status': 'Hiatus',
                'genres': ['Action', 'Fantasy', 'Adventure']
            },
            {
                'title': 'The Case of the Missing Artifact',
                'description': 'A brilliant but eccentric investigator takes on a case that baffles the police.',
                'cover_image_url': 'https://placehold.co/400x600/0000FF/FFFFFF?text=Missing+Artifact',
                'status': 'Ongoing',
                'genres': ['Mystery', 'Detective']
            },
            {
                'title': 'Reborn as a Duke\'s Scion',
                'description': 'A modern person finds themselves reincarnated into a noble family in a fantasy world.',
                'cover_image_url': 'https://placehold.co/400x600/4B0082/FFFFFF?text=Duke+Scion',
                'status': 'Ongoing',
                'genres': ['Regression', 'Fantasy', 'Adventure']
            },
            {
                'title': 'School Life Comedy',
                'description': 'Follows the hilarious antics of a group of friends navigating their unpredictable school days.',
                'cover_image_url': 'https://placehold.co/400x600/FFFF00/000000?text=School+Comedy',
                'status': 'Completed',
                'genres': ['Slice of Life', 'Comedy']
            },
            {
                'title': 'Shadows Over Silverwood',
                'description': 'A dark secret looms over a peaceful town as strange events begin to unfold.',
                'cover_image_url': 'https://placehold.co/400x600/36454F/FFFFFF?text=Silverwood',
                'status': 'Ongoing',
                'genres': ['Mystery', 'Thriller']
            },
            {
                'title': 'The Second Chance Chef',
                'description': 'A renowned chef loses everything and starts anew, rediscovering his passion for cooking and life.',
                'cover_image_url': 'https://placehold.co/400x600/A52A2A/FFFFFF?text=Second+Chef',
                'status': 'Ongoing',
                'genres': ['Slice of Life', 'Drama']
            },
        ]

        series_objects = {}
        for series_info in series_data:
            genre_list = series_info.pop('genres')
            series, created = Series.objects.get_or_create(
                title=series_info['title'],
                defaults=series_info
            )
            series_objects[series.title] = series
            
            if created:
                # Add genres
                for genre_name in genre_list:
                    series.genres.add(genres[genre_name])
                self.stdout.write(self.style.SUCCESS(f'Created series: {series.title}'))

        # Create chapters
        chapters_data = [
            {
                'series': 'The Crimson Blade',
                'chapter_number': 1,
                'title': 'The First Trial',
                'content': 'The searing heat of the desert wind...',
                'word_count': 1500,
                'days_ago': 10
            },
            {
                'series': 'The Crimson Blade',
                'chapter_number': 2,
                'title': 'Ambush in the Oasis',
                'content': 'Water, a mirage in the shifting sands...',
                'word_count': 1800,
                'days_ago': 8
            },
            {
                'series': 'Whispers in the Library',
                'chapter_number': 1,
                'title': 'Dusty Tomes and Dark Secrets',
                'content': 'The old library creaked with forgotten tales...',
                'word_count': 1200,
                'days_ago': 7
            },
            {
                'series': 'Back to My 18th Life',
                'chapter_number': 1,
                'title': 'Waking Up in My Old Uniform',
                'content': 'The blaring alarm clock was familiar, too familiar...',
                'word_count': 2000,
                'days_ago': 5
            },
            {
                'series': 'My Quiet Corner Cafe',
                'chapter_number': 1,
                'title': 'First Brew of the Day',
                'content': 'The aroma of freshly ground coffee beans...',
                'word_count': 900,
                'days_ago': 3
            },
            {
                'series': 'Echoes of the Forgotten Empire',
                'chapter_number': 1,
                'title': 'The Lost City',
                'content': 'Rumors of a city swallowed by the jungle...',
                'word_count': 2200,
                'days_ago': 6
            },
            {
                'series': 'The Case of the Missing Artifact',
                'chapter_number': 1,
                'title': 'The Empty Pedestal',
                'content': 'The museum curator paced frantically...',
                'word_count': 1300,
                'days_ago': 4
            },
            {
                'series': 'Reborn as a Duke\'s Scion',
                'chapter_number': 1,
                'title': 'A New Life, A New Name',
                'content': 'He opened his eyes to a lavish canopy...',
                'word_count': 1900,
                'days_ago': 2
            },
            {
                'series': 'School Life Comedy',
                'chapter_number': 1,
                'title': 'The Exploding Volcano Project',
                'content': 'Our science fair project had a minor hiccup...',
                'word_count': 1000,
                'days_ago': 1
            },
            {
                'series': 'Shadows Over Silverwood',
                'chapter_number': 1,
                'title': 'The Old Mill',
                'content': 'The moon cast long shadows over the abandoned mill...',
                'word_count': 1600,
                'days_ago': 9
            },
            {
                'series': 'The Second Chance Chef',
                'chapter_number': 1,
                'title': 'A Dish Called Hope',
                'content': 'He held the worn spatula, his hands trembling...',
                'word_count': 1100,
                'days_ago': 0
            },
        ]

        for chapter_info in chapters_data:
            series_title = chapter_info.pop('series')
            days_ago = chapter_info.pop('days_ago')
            
            publication_date = timezone.now() - timedelta(days=days_ago)
            
            chapter, created = Chapter.objects.get_or_create(
                series=series_objects[series_title],
                chapter_number=chapter_info['chapter_number'],
                defaults={
                    **chapter_info,
                    'publication_date': publication_date
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created chapter: {series_title} - Chapter {chapter.chapter_number}'
                ))

        self.stdout.write(self.style.SUCCESS('Test data loaded successfully!'))
