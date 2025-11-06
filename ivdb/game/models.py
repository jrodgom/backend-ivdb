from django.db import models

# Create your models here.
class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    platform = models.CharField(max_length=100, blank=True)
    developer = models.CharField(max_length=100, blank=True)
    cover_image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title