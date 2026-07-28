# TrueCheck - Professional Background Verification Platform

A Django-based background verification platform powered by TrueTrace Solutions.

## Features

- Professional background check services
- Multiple verification types (Criminal, Employment, Education, Reference, Identity, Medical)
- Secure user authentication with email login
- Dashboard for check management
- Admin interface for verification management
- Responsive design for desktop and mobile

## Admin Credentials

**Default Admin Access:**
- **Username:** `admin1`
- **Email:** `admin@vericheck.com`
- **Password:** `adim123`

**Access Points:**
- Django Admin: `/admin/`
- Custom Admin Dashboard: `/admin-dashboard/`

Both use the same credentials.

---

## Local Development Setup

### Prerequisites
- Python 3.10+
- pip
- Virtual environment (venv)

### Installation Steps

1. **Clone/Setup the project:**
```bash
cd Background_check
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create .env file (optional for local dev):**
```bash
# Copy from .env.example
cp .env.example .env
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser (if needed):**
```bash
python setup_superuser.py
```

Or use Django's management command:
```bash
python manage.py createsuperuser
```

7. **Collect static files:**
```bash
python manage.py collectstatic --noinput
```

8. **Run development server:**
```bash
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000` in your browser.

---

## Production Deployment (Render)

### Step 1: Prepare Repository

Ensure you have:
- `requirements.txt` ✓
- `build.sh` ✓
- `render.yaml` ✓
- `.env.example` ✓

### Step 2: Set Environment Variables on Render

In your Render Web Service settings, add these environment variables:

```
DEBUG=False
SECRET_KEY=[Generate a strong secret key]
DATABASE_URL=[Automatically set by Render if using PostgreSQL]
ADMIN_EMAIL=admin@vericheck.com
ADMIN_USERNAME=admin1
ADMIN_PASSWORD=[Your secure password]
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=[Your Gmail]
EMAIL_HOST_PASSWORD=[Your Gmail App Password]
DEFAULT_FROM_EMAIL=noreply@truecheck.com
```

### Step 3: Configure Render PostgreSQL Database

1. Create a PostgreSQL database in Render
2. Render will automatically set `DATABASE_URL` environment variable
3. The app will automatically use PostgreSQL when `DATABASE_URL` is present

### Step 4: Deploy

1. Push code to GitHub
2. Connect Render to your GitHub repository
3. Render will automatically:
   - Run `build.sh` command
   - Apply migrations
   - Create superuser with provided credentials
   - Collect static files
   - Start the Gunicorn server

### Accessing Your Deployment

- **Application:** `https://your-render-domain.onrender.com`
- **Admin Panel:** `https://your-render-domain.onrender.com/admin/`
- **Custom Admin:** `https://your-render-domain.onrender.com/admin-dashboard/`
- **Login with:** Username `admin1` or Email `admin@vericheck.com`

---

## How the Application Handles Different Environments

### Local Development (SQLite)
- Uses SQLite database by default
- `DEBUG=True`
- Email sends to console
- No `DATABASE_URL` set

### Production (Render with PostgreSQL)
- Automatically detects `DATABASE_URL`
- Uses PostgreSQL driver (`psycopg2-binary`)
- `DEBUG=False`
- SSL/TLS enabled for secure connections
- Static files served by WhiteNoise
- Admin user auto-created from environment variables

### Automatic Configuration

The app automatically detects its environment:
- **If `DATABASE_URL` exists:** Uses PostgreSQL
- **If `DATABASE_URL` is empty:** Uses SQLite
- **If `DEBUG=True`:** Runs in development mode
- **If `DEBUG=False`:** Runs in production mode with security hardening

---

## File Structure

```
Background_check/
├── core/                          # Main app
│   ├── models.py                  # Database models
│   ├── views.py                   # View logic
│   ├── urls.py                    # URL routing
│   ├── admin.py                   # Custom admin interface
│   └── templates/
│       └── core/                  # HTML templates
├── Truecheck/                     # Project settings
│   ├── settings.py                # Django settings (ENV-aware)
│   ├── urls.py                    # Main URL config
│   └── wsgi.py                    # WSGI application
├── static/                        # CSS, JS, images
├── templates/                     # Base templates
├── manage.py                      # Django management
├── requirements.txt               # Python dependencies
├── setup_superuser.py             # Admin user setup
├── build.sh                       # Render build script
├── render.yaml                    # Render configuration
├── Procfile                       # Alternative deployment config
├── .env.example                   # Environment variables template
└── db.sqlite3                     # Local database (git ignored)
```

---

## Credentials Management

### Local Development
Edit credentials in `.env.example` or in `setup_superuser.py`:
```python
email = 'admin@vericheck.com'
username = 'admin1'
password = 'adim123'
```

### Production (Render)
Set these as environment variables in Render dashboard:
```
ADMIN_EMAIL=admin@vericheck.com
ADMIN_USERNAME=admin1
ADMIN_PASSWORD=your_secure_password
```

The `build.sh` script will automatically:
1. Read these environment variables
2. Create the superuser during deployment
3. Use these same credentials for both Django Admin and Custom Admin

---

## Database Management

### Local (SQLite)
- Stored in `db.sqlite3`
- No configuration needed
- Perfect for development

### Production (Render PostgreSQL)
- Render creates PostgreSQL instance
- Connection string stored in `DATABASE_URL` environment variable
- App automatically configures connection pooling
- Migrations run automatically during build

---

## Static Files

### Local Development
- Served automatically by Django development server
- Location: `static/` directory

### Production (Render)
- Collected to `staticfiles/` during build
- Served by WhiteNoise middleware
- Compressed and cached for performance

---

## Email Configuration

### Local Development (Console)
By default, emails print to console for testing

### Production (Gmail SMTP)
Configure environment variables:
```
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Not your Gmail password!
```

To generate Gmail App Password:
1. Enable 2-Factor Authentication
2. Go to Google Account settings
3. Create an App Password
4. Use this 16-character password in environment variable

---

## Troubleshooting

### Static Files Not Loading
```bash
# Collect static files again
python manage.py collectstatic --noinput
```

### Migrations Failing
```bash
# Check migration status
python manage.py showmigrations

# Migrate manually
python manage.py migrate
```

### Admin Access Issues
- Check environment variables are set correctly
- Run `python setup_superuser.py` to recreate admin user
- Access `/admin/` for Django admin or `/admin-dashboard/` for custom admin

### Database Connection Error
- Verify `DATABASE_URL` is set correctly on Render
- Check Render PostgreSQL instance is running
- Test connection in Render dashboard

---

## Security Notes

1. **Never commit** `.env` file or database files
2. Change `SECRET_KEY` for production
3. Set `DEBUG=False` on production
4. Use strong `ADMIN_PASSWORD`
5. Generate secure credentials for Render
6. Regularly update dependencies

---

## Support & Documentation

- Django: https://www.djangoproject.com/
- Render: https://render.com/docs
- PostgreSQL: https://www.postgresql.org/

---

## License

© 2024 TrueTrace Solutions. All rights reserved.
