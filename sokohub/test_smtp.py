import os
import django
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sokohub.settings')
django.setup()

def test_email():
    try:
        subject = "Soko Hub SMTP Test"
        message = "This is a test email to confirm your SMTP configuration is working."
        recipient = os.getenv('EMAIL_HOST_USER') # Send to self
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
        print(f"Successfully sent test email to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

if __name__ == '__main__':
    test_email()
