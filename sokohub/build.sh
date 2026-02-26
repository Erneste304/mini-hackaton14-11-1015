#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Clean up manually created tables from previous fixes if they exist, so standard migrations can run cleanly
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sokohub.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS socialaccount_socialapp_sites CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS django_site CASCADE;')
        cursor.execute("DELETE FROM django_migrations WHERE app='sites';")
except Exception as e:
    print('Cleanup skipped or failed:', e)
"

# Run normal Django migrations
python manage.py migrate

python manage.py showmigrations
