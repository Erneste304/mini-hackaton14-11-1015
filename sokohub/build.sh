#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Automatically fix inconsistent migration history on Render if it occurs
python fix_render_db.py
python fix_social_sites_table.py

python manage.py migrate
