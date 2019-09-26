release: python manage.py db upgrade
web: gunicorn wsgi:app --workers=1 --access-logfile=-
