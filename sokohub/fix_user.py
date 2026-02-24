import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sokohub.settings')
django.setup()

from accounts.models import User

def fix_password(username, password):
    try:
        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()
        print(f"Successfully set password for user '{username}'.")
        print(f"Has Usable Password now: {u.has_usable_password()}")
    except User.DoesNotExist:
        print(f"User '{username}' does not exist.")

if __name__ == '__main__':
    fix_password('Erneste', 'qqqqqqqqq')
