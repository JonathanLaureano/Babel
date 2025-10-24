# Babel
An app for reading machine translated novels. A python django backend and an angular typescript front end.

## Setup

### Backend Setup
1. Navigate to the Backend directory:
   ```sh
   cd Backend
   ```

2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure it:
   ```sh
   cp .env.example .env
   # Edit .env with your database credentials and secret key
   ```

5. Run migrations:
   ```sh
   python manage.py migrate
   ```

6. Start the development server:
   ```sh
   python manage.py runserver
   ```
