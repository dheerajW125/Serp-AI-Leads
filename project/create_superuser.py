import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")  # Replace with your actual settings module
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@gamil.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Asdf1234@#")

if not User.objects.filter(username=username).exists():
    print("Creating superuser...")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print("Superuser already exists.")
