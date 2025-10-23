# Babel
An app for reading machine translated novels. A python django backend and an angular typescript front end.

## Project Structure
```
Babel/
├── backend/          # Django REST API
│   ├── backend/      # Django project settings
│   ├── novels/       # Main app for novels and chapters
│   └── manage.py
└── frontend/         # Angular application
    └── src/
        └── app/
```

## Prerequisites
- Python 3.8+
- Node.js 18+
- npm 8+

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

5. Start the Django development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the Angular development server:
```bash
ng serve
```

The application will be available at `http://localhost:4200/`

## API Endpoints

- `GET /api/novels/` - List all novels
- `GET /api/novels/{id}/` - Get novel details
- `POST /api/novels/` - Create a new novel
- `PUT /api/novels/{id}/` - Update a novel
- `DELETE /api/novels/{id}/` - Delete a novel
- `GET /api/chapters/` - List all chapters
- `GET /api/chapters/?novel={id}` - List chapters for a specific novel
- `GET /api/chapters/{id}/` - Get chapter details
- `POST /api/chapters/` - Create a new chapter
- `PUT /api/chapters/{id}/` - Update a chapter
- `DELETE /api/chapters/{id}/` - Delete a chapter

## Development

### Running Both Servers

1. Start the backend (in one terminal):
```bash
cd backend && python manage.py runserver
```

2. Start the frontend (in another terminal):
```bash
cd frontend && ng serve
```

### Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to manage novels and chapters.

## Features

- Browse machine translated novels
- View novels with their chapters
- Read original and translated content side by side
- REST API for CRUD operations on novels and chapters
- CORS enabled for frontend-backend communication

