# SelfBlog — Backend (Django)

Django REST API backend for the SelfBlog project.

## Prerequisites
- Python 3.10+ (recommend 3.11+)
- pip
- Virtual environment tool (venv or virtualenv)
- Optional: PostgreSQL or other production DB

## Quick start (development)
1. Create and activate a virtualenv

```bash
cd backend_self_blog
python -m venv env
# Windows
env\Scripts\activate
# macOS / Linux
# source env/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create a `.env` file at the project root (see example below)

4. Apply migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/` by default.

## .env (example)
Create `backend_self_blog/.env` and add your sensitive values. Example values used by this project:

```
# Django security
SECRET_KEY=replace-this-with-a-strong-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (optional - default is sqlite)
# DATABASE_ENGINE=django.db.backends.postgresql
# DATABASE_NAME=your_db
# DATABASE_USER=your_user
# DATABASE_PASSWORD=your_password
# DATABASE_HOST=localhost
# DATABASE_PORT=5432

# Cloudinary (media storage)
CLOUDINARY_CLOUD_NAME=dtxh9hjpd
CLOUDINARY_API_KEY=689746391593673
CLOUDINARY_API_SECRET=W4DXthKN65cbhFKarP7tlns1AsA

# Email (SMTP)
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-email-password

# Frontend URL for password reset links
FRONTEND_URL=http://localhost:5173
```

The project uses `python-dotenv` to load `.env` into `os.environ`.

## Important settings
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` are loaded from environment.
- Cloudinary credentials are read from env and used as `DEFAULT_FILE_STORAGE`.
- JWT settings live in `SIMPLE_JWT` in `backend/settings.py`.
- REST framework uses `rest_framework_simplejwt` for authentication.

## Common manage.py commands
- `python manage.py migrate` — run DB migrations
- `python manage.py createsuperuser` — create admin user
- `python manage.py runserver` — start dev server
- `python manage.py collectstatic` — collect static files for production
- `python manage.py loaddata <fixture>` — load fixture data

## Running tests

```bash
python manage.py test
```

## Deployment notes
- Set `DEBUG=False` in production and configure `ALLOWED_HOSTS`.
- Use PostgreSQL (or preferred production DB) configured through env variables.
- Use a WSGI/ASGI server (Gunicorn + Daphne/uvicorn depending on needs).
- Configure static file serving (whitenoise or CDN) and media storage (Cloudinary).
- Securely store environment variables (secrets manager or environment provisioning).

## CORS / Frontend
- The frontend expects the backend API under `/api/v1` (see `VITE_API_URL` in frontend `.env`).
- Ensure `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` include your frontend origin(s).

## Troubleshooting
- If you change `.env`, restart the dev server.
- If migrations fail, inspect the migration files in `api/migrations/`.
- For email issues, verify SMTP credentials and allow less secure apps if needed (or use app passwords).

---
