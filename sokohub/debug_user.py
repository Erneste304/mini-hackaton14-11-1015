import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sokohub.settings')
django.setup()

from accounts.models import User

def check_user(username):
    try:
        u = User.objects.get(username=username)
        print(f"User: {u.username}")
        print(f"Email: {u.email}")
        print(f"Has Usable Password: {u.has_usable_password()}")
        print(f"Is Active: {u.is_active}")
        
        # Test password if we knew it, but we don't.
        # But we can check if it's hashed.
        print(f"Password Hashed: {u.password.startswith('pbkdf2_') or u.password.startswith('argon2')}")
        
    except User.DoesNotExist:
        print(f"User '{username}' does not exist.")

if __name__ == '__main__':
    check_user('Erneste')
