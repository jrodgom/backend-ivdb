from django.db import models

class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    platform = models.CharField(max_length=100, blank=True)
    developer = models.CharField(max_length=100, blank=True)
    cover_image = models.URLField(blank=True)
    metacritic = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    minimum_requirements = models.JSONField(null=True, blank=True)
    recommended_requirements = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title