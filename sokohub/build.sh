#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# 1. Pre-migration: fake the sites migration record so allauth doesn't error
python setup_render.py pre

# 2. Run all Django migrations
python manage.py migrate --run-syncdb

# 3. Post-migration: ensure Site ID=1 has correct domain + Google SocialApp is configured
python setup_render.py post

# 4. Show migration status for debugging in Render logs
python manage.py showmigrations
