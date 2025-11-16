from django_filters import rest_framework as filters
from game.models import Game
from django.db.models import Avg

class GameFilter(filters.FilterSet):
    genre = filters.CharFilter(method='filter_genre')
    platform = filters.CharFilter(method='filter_platform')
    min_rating = filters.NumberFilter(method='filter_min_rating')
    max_rating = filters.NumberFilter(method='filter_max_rating')
    min_metacritic = filters.NumberFilter(field_name='metacritic', lookup_expr='gte')
    max_metacritic = filters.NumberFilter(field_name='metacritic', lookup_expr='lte')
    
    class Meta:
        model = Game
        fields = []
    
    def filter_genre(self, queryset, name, value):
        """Filtrar por género (búsqueda parcial, case-insensitive)"""
        return queryset.filter(genre__icontains=value)
    
    def filter_platform(self, queryset, name, value):
        """Filtrar por plataforma (búsqueda parcial, case-insensitive)"""
        return queryset.filter(platform__icontains=value)
    
    def filter_min_rating(self, queryset, name, value):
        """Filtrar por rating mínimo basado en average_rating de reviews"""
        from review.models import Review
        from django.db.models import Avg, Q
        
        # Obtener IDs de juegos que cumplen con el rating mínimo
        games_with_rating = Review.objects.values('game_id').annotate(
            avg_rating=Avg('rating')
        ).filter(avg_rating__gte=value).values_list('game_id', flat=True)
        
        return queryset.filter(id__in=games_with_rating)
    
    def filter_max_rating(self, queryset, name, value):
        """Filtrar por rating máximo basado en average_rating de reviews"""
        from review.models import Review
        from django.db.models import Avg, Q
        
        # Obtener IDs de juegos que cumplen con el rating máximo
        games_with_rating = Review.objects.values('game_id').annotate(
            avg_rating=Avg('rating')
        ).filter(avg_rating__lte=value).values_list('game_id', flat=True)
        
        return queryset.filter(id__in=games_with_rating)
