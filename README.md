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



### Frontend Setup

This project was generated using [Angular CLI](https://github.com/angular/angular-cli) version 20.3.7.

1. Navigate to the Frontend directory:
   ```bash
   cd Frontend/babelUI
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Install date-fns for accurate date formatting:
   ```bash
   npm install date-fns
   ```

4. Start a local development server:
   ```bash
   ng serve
   ```

Once the server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files.

#### Code scaffolding

Angular CLI includes powerful code scaffolding tools. To generate a new component, run:

```bash
ng generate component component-name
```

For a complete list of available schematics (such as `components`, `directives`, or `pipes`), run:

```bash
ng generate --help
```

#### Building

To build the project run:

```bash
ng build
```

This will compile your project and store the build artifacts in the `dist/` directory. By default, the production build optimizes your application for performance and speed.

#### Running unit tests

To execute unit tests with the [Karma](https://karma-runner.github.io) test runner, use the following command:

```bash
ng test
```

#### Running end-to-end tests

For end-to-end (e2e) testing, run:

```bash
ng e2e
```

Angular CLI does not come with an end-to-end testing framework by default. You can choose one that suits your needs.

#### Additional Resources

For more information on using the Angular CLI, including detailed command references, visit the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.
