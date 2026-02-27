import os
import sys
import django

# Set up Django environment manually for the external script
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sokohub.settings")
django.setup()

from django.db import connection

def setup_db():
    print("STEP 1: Checking and preparing django_site table and faking sites.0001_initial migration...")
    
    try:
        with connection.cursor() as cursor:
            # Create django_site if it completely doesn't exist
            if connection.vendor == 'sqlite':
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS django_site (
                        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        domain varchar(100) NOT NULL UNIQUE,
                        name varchar(50) NOT NULL
                    );
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS django_site (
                        id SERIAL PRIMARY KEY,
                        domain VARCHAR(100) NOT NULL UNIQUE,
                        name VARCHAR(50) NOT NULL
                    );
                """)
            
            # Fake the migration record to bypass InconsistentMigrationHistory
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'sites', '0001_initial', CURRENT_TIMESTAMP
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations WHERE app = 'sites' AND name = '0001_initial'
                );
            """)
            print("Successfully secured sites migration history!")

    except Exception as e:
        print(f"Error preparing sites migration: {e}")

def create_socialaccount_sites_table():
    print("STEP 2: Ensuring socialaccount_socialapp_sites table exists...")

    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'sqlite':
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
                        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        socialapp_id integer NOT NULL REFERENCES socialaccount_socialapp (id) DEFERRABLE INITIALLY DEFERRED,
                        site_id integer NOT NULL REFERENCES django_site (id) DEFERRABLE INITIALLY DEFERRED
                    );
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
                        id SERIAL PRIMARY KEY,
                        socialapp_id integer NOT NULL REFERENCES socialaccount_socialapp (id) DEFERRABLE INITIALLY DEFERRED,
                        site_id integer NOT NULL REFERENCES django_site (id) DEFERRABLE INITIALLY DEFERRED
                    );
                """)
            
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS socialaccount_socialapp_sites_socialapp_id_site_id_uniq 
                ON socialaccount_socialapp_sites (socialapp_id, site_id);
            """)
            print("Successfully ensured socialaccount_socialapp_sites table exists!")
            
    except Exception as e:
        print(f"Error ensuring socialaccount_socialapp_sites exists (this is normal if socialaccount tables haven't migrated yet): {e}")

def ensure_site_1():
    print("STEP 3: Ensuring Site with ID 1 exists to fix the 500 error on the login page...")
    
    from django.contrib.sites.models import Site
    try:
        site, created = Site.objects.get_or_create(
            id=1, 
            defaults={'domain': 'example.com', 'name': 'example.com'}
        )
        if created:
            print("Created Site ID=1 successfully!")
        else:
            print(f"Site ID=1 already exists as {site.domain}!")
    except Exception as e:
        print(f"Failed to use Django ORM to create Site ID 1: {e}")
        print("Falling back to raw SQL...")
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'sqlite':
                    cursor.execute("INSERT OR IGNORE INTO django_site (id, domain, name) VALUES (1, 'example.com', 'example.com');")
                else:
                    cursor.execute("INSERT INTO django_site (id, domain, name) VALUES (1, 'example.com', 'example.com') ON CONFLICT (domain) DO UPDATE SET id=1;")
            print("Forced Site ID 1 via raw SQL!")
        except Exception as sql_e:
            print(f"Failed to force insert Site ID 1: {sql_e}")

if __name__ == "__main__":
    if "POST_MIGRATE" in os.environ:
        create_socialaccount_sites_table()
        ensure_site_1()
    else:
        setup_db()
