from django.db import models
from django.contrib.auth.models import User
from game.models import Game


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')  # Un usuario solo puede marcar un juego como favorito una vez
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"
