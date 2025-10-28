# Babel Angular UI

A modern Angular application for reading machine-translated novels, built following Angular best practices and the Tour of Heroes architecture.

## Architecture

This application follows a component-based architecture with:

### Components

1. **SeriesListComponent** (`/`)
   - Displays a grid of available novel series
   - Shows series title, cover image, status, genre tags, and chapter count
   - Provides navigation to individual series details

2. **SeriesDetailComponent** (`/series/:id`)
   - Displays detailed information about a specific series
   - Lists all available chapters with metadata
   - Provides navigation to chapter reader

3. **ChapterReaderComponent** (`/chapter/:id`)
   - Displays the full content of a chapter
   - Provides previous/next chapter navigation
   - Shows chapter metadata (word count, publication date)
   - Easy navigation back to series details

### Services

- **LibraryService**: Handles all HTTP communication with the Django REST API
  - Series CRUD operations
  - Chapter retrieval and navigation
  - Genre management

### Models

TypeScript interfaces that mirror the Django backend models:
- `Genre`: Genre categories
- `Series`: Novel series with metadata
- `Chapter`: Individual chapter content

## Features

- **Responsive Design**: Works on desktop and mobile devices
- **Clean Navigation**: Easy-to-use header with routing
- **Status Indicators**: Visual badges for series status (Ongoing, Completed, Hiatus)
- **Genre Tags**: Quick filtering by genre
- **Chapter Navigation**: Sequential reading with prev/next buttons
- **Error Handling**: User-friendly error messages for API failures

## API Integration

The application is configured to connect to the Django backend at `http://localhost:8000/api/library/`

Endpoints used:
- `GET /series/` - List all series
- `GET /series/:id/` - Get series details
- `GET /series/:id/chapters/` - Get chapters for a series
- `GET /chapters/:id/` - Get chapter content
- `GET /chapters/:id/next/` - Get next chapter
- `GET /chapters/:id/previous/` - Get previous chapter
- `GET /genres/` - List all genres

## Development

### Running the Development Server

```bash
cd Frontend/babelUI
npm install
npm start
```

Navigate to `http://localhost:4200/`. The application will automatically reload if you change any source files.

### Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

### Running Tests

```bash
npm test
```

All components and services have unit tests using Jasmine and Karma.

## Project Structure

```
src/app/
├── components/
│   ├── series-list/       # Home page with series grid
│   ├── series-detail/     # Series details with chapter list
│   └── chapter-reader/    # Chapter reading view
├── models/                # TypeScript interfaces
│   ├── genre.ts
│   ├── series.ts
│   └── chapter.ts
├── services/              # API communication
│   └── library.service.ts
├── app.config.ts          # Application configuration
├── app.routes.ts          # Routing configuration
├── app.html               # Root template with navigation
└── app.ts                 # Root component
```

## Styling

The application uses a modern, clean design with:
- Gradient-based navigation header
- Card-based layouts for content
- Responsive grid systems
- Smooth transitions and hover effects
- Readable typography for long-form content

## Future Enhancements

Potential improvements could include:
- User authentication and reading progress tracking
- Bookmarking favorite series
- Search and advanced filtering
- Dark mode support
- Offline reading capabilities
- Comments and ratings system
