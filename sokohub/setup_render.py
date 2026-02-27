"""
setup_render.py - Run after migrations on Render to fix DB state.
This ensures:
1. Site ID=1 exists with the correct Render domain
2. The Google SocialApp exists and is linked to Site ID=1
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sokohub.settings")
django.setup()

from django.db import connection


def ensure_site():
    """Ensure Site ID=1 exists with the correct domain."""
    print("--- Ensuring django_site record exists ---")
    from django.contrib.sites.models import Site

    render_hostname = os.environ.get(
        'RENDER_EXTERNAL_HOSTNAME',
        'mini-hackaton14-11-1015.onrender.com'
    )

    try:
        site = Site.objects.get(id=1)
        # Update domain if it's still the placeholder
        if site.domain in ('example.com', 'example.fr', ''):
            site.domain = render_hostname
            site.name = 'SokoHub'
            site.save()
            print(f"Updated Site ID=1 domain to: {render_hostname}")
        else:
            print(f"Site ID=1 already set to: {site.domain}")
    except Site.DoesNotExist:
        Site.objects.create(id=1, domain=render_hostname, name='SokoHub')
        print(f"Created Site ID=1 with domain: {render_hostname}")
    except Exception as e:
        print(f"ORM failed for site, trying raw SQL: {e}")
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO django_site (id, domain, name)
                VALUES (1, %s, 'SokoHub')
                ON CONFLICT (id) DO UPDATE SET domain = EXCLUDED.domain, name = EXCLUDED.name;
            """, [render_hostname])
        print(f"Raw SQL: set Site ID=1 to {render_hostname}")


def ensure_google_socialapp():
    """Ensure Google SocialApp is configured and linked to Site ID=1."""
    print("--- Ensuring Google SocialApp exists ---")

    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    secret = os.environ.get('GOOGLE_SECRET', '')

    if not client_id or not secret:
        print("WARNING: GOOGLE_CLIENT_ID or GOOGLE_SECRET not set. Skipping SocialApp setup.")
        return

    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site

        site = Site.objects.get(id=1)

        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': secret,
            }
        )

        if not created:
            # Update credentials in case they changed
            app.client_id = client_id
            app.secret = secret
            app.save()

        # Link to site if not already
        if site not in app.sites.all():
            app.sites.add(site)
            print("Linked Google SocialApp to Site ID=1")
        else:
            print("Google SocialApp already linked to Site ID=1")

        print(f"Google SocialApp OK (client_id={client_id[:20]}...)")

    except Exception as e:
        print(f"Failed to set up Google SocialApp: {e}")
        import traceback
        traceback.print_exc()


def fake_sites_migration_if_needed():
    """Insert the sites 0001_initial migration row if missing (pre-migrate step)."""
    print("--- Checking sites migration history ---")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'sites', '0001_initial', NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations
                    WHERE app = 'sites' AND name = '0001_initial'
                );
            """)
        print("Sites migration history OK")
    except Exception as e:
        print(f"Could not check sites migration (may not exist yet): {e}")


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'post'

    if mode == 'pre':
        # Before migrations: just fake the sites record in django_migrations
        fake_sites_migration_if_needed()
    else:
        # After migrations: ensure site and social app are set up
        ensure_site()
        ensure_google_socialapp()
        print("--- Setup complete ---")
