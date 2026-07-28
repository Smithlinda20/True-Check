web: gunicorn Truecheck.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate && python setup_superuser.py
