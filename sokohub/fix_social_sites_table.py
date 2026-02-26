import os
import sys
import django
from django.db import connection

# Set up Django environment manually for the external script
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sokohub.settings")
django.setup()

def fix_social_sites_table():
    print("Connecting to the database to create missing socialaccount_socialapp_sites table...")
    
    with connection.cursor() as cursor:
        try:
            # Check if using SQLite or Postgres to apply correct syntax
            if connection.vendor == 'sqlite':
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
                        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        socialapp_id integer NOT NULL REFERENCES socialaccount_socialapp (id) DEFERRABLE INITIALLY DEFERRED,
                        site_id integer NOT NULL REFERENCES django_site (id) DEFERRABLE INITIALLY DEFERRED
                    );
                """)
            else:
                # Postgres Syntax
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
                        id SERIAL PRIMARY KEY,
                        socialapp_id integer NOT NULL REFERENCES socialaccount_socialapp (id) DEFERRABLE INITIALLY DEFERRED,
                        site_id integer NOT NULL REFERENCES django_site (id) DEFERRABLE INITIALLY DEFERRED
                    );
                """)
                
            # Create Unique Index (Standard SQL)
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS socialaccount_socialapp_sites_socialapp_id_site_id_uniq 
                ON socialaccount_socialapp_sites (socialapp_id, site_id);
            """)
            print("Successfully created the missing table!")
            
        except Exception as e:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    fix_social_sites_table()
