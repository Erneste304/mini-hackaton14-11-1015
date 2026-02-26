import os
import sys
import django
from django.db import connection

# Set up Django environment manually for the external script
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sokohub.settings")
django.setup()

def fake_sites_migration():
    print("Connecting to the database to fake the 'sites' migration...")
    
    with connection.cursor() as cursor:
        # Create the django_site table manually if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_site (
                id SERIAL PRIMARY KEY,
                domain VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(50) NOT NULL
            );
        """)
        
        # Insert a default site if empty
        cursor.execute("SELECT COUNT(*) FROM django_site;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO django_site (domain, name) VALUES ('example.com', 'example.com');")
        
        # Manually insert the migration record to trick Django
        # so it thinks 'sites' 0001_initial was applied *before* 'socialaccount'
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            SELECT 'sites', '0001_initial', NOW()
            WHERE NOT EXISTS (
                SELECT 1 FROM django_migrations WHERE app = 'sites' AND name = '0001_initial'
            );
        """)
        
    print("Successfully faked the sites migration! Try deploying again.")

if __name__ == "__main__":
    fake_sites_migration()
