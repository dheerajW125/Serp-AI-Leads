from django.db import models

# Create your models here.
class ScrapedLink(models.Model):
    url = models.URLField(unique=True)
    created = models.DateTimeField(auto_now_add=True)  # Set once when created
    updated = models.DateTimeField(auto_now=True)      # Updated every time saved

    def __str__(self):
        return self.url