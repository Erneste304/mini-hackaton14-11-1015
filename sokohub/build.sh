#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# 1. First, fake apply sites to prevent the socialaccount dependency error
python db_fix.py

# 2. Run normal Django migrations. This creates socialaccount tables if they don't exist.
python manage.py migrate

# 3. Create socialaccount_socialapp_sites M2M table AND ensure Site ID=1 exists to fix 500 error!
POST_MIGRATE=1 python db_fix.py

# 4. Print migrations for debugging via Render logs
python manage.py showmigrations
