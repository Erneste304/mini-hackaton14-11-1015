import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sokohub.settings")
django.setup()

from django.db import connection

def setup_db():
    print("STEP 1: Faking sites migration...")
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'sqlite':
                cursor.execute("CREATE TABLE IF NOT EXISTS django_site (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, domain varchar(100) NOT NULL UNIQUE, name varchar(50) NOT NULL);")
            else:
                cursor.execute("CREATE TABLE IF NOT EXISTS django_site (id SERIAL PRIMARY KEY, domain VARCHAR(100) NOT NULL UNIQUE, name VARCHAR(50) NOT NULL);")
            cursor.execute("INSERT INTO django_migrations (app, name, applied) SELECT 'sites', '0001_initial', CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT 1 FROM django_migrations WHERE app = 'sites' AND name = '0001_initial');")
            print("Successfully secured sites migration history!")
    except Exception as e:
        print("Error preparing sites migration:", e)

def create_socialaccount_sites_table():
    print("STEP 2: Ensuring socialaccount_socialapp_sites table exists...")
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'sqlite':
                cursor.execute("CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, socialapp_id integer NOT NULL REFERENCES socialaccount_socialapp (id) DEFERRABLE INITIALLY DEFERRED, site_id integer NOT NULL REFERENCES django_site (id) DEFERRABLE INITIALLY DEFERRED);")
            else:
                cursor.execute("CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (id SERIAL PRIMARY KEY, socialapp_id integer NOT NULL REFERENCES socialaccount_socialapp (id) DEFERRABLE INITIALLY DEFERRED, site_id integer NOT NULL REFERENCES django_site (id) DEFERRABLE INITIALLY DEFERRED);")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS socialaccount_socialapp_sites_socialapp_id_site_id_uniq ON socialaccount_socialapp_sites (socialapp_id, site_id);")
            print("Successfully ensured socialaccount_socialapp_sites table exists!")
    except Exception as e:
        print("Error ensuring socialaccount_socialapp_sites exists:", e)

def ensure_site_1():
    print("STEP 3: Ensuring Site with ID 1 exists...")
    from django.contrib.sites.models import Site
    try:
        site, created = Site.objects.get_or_create(id=1, defaults={'domain': 'example.com', 'name': 'example.com'})
        print("Site ID=1 exists successfully!")
    except Exception as e:
        print("Failed to get/create site:", e)

if __name__ == "__main__":
    if os.environ.get("POST_MIGRATE") == "1":
        create_socialaccount_sites_table()
        ensure_site_1()
    else:
        setup_db()
