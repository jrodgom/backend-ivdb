from rest_framework import serializers
from game.models import Game
from django.db.models import Avg, Count

class GameSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = ['id', 'title', 'description', 'release_date', 'genre', 'platform', 
                  'developer', 'cover_image', 'metacritic', 'rating', 'created_at',
                  'minimum_requirements', 'recommended_requirements',
                  'average_rating', 'review_count']
    
    def get_average_rating(self, obj):
        """Calcular rating promedio de las reviews del juego"""
        from review.models import Review
        avg = Review.objects.filter(game=obj).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    def get_review_count(self, obj):
        """Contar número de reviews del juego"""
        from review.models import Review
        return Review.objects.filter(game=obj).count()