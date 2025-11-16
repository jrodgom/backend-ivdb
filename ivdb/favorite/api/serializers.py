from rest_framework import serializers
from favorite.models import Favorite
from game.models import Game


class GameBasicSerializer(serializers.ModelSerializer):
    """Serializer simplificado para incluir en favoritos"""
    class Meta:
        model = Game
        fields = ['id', 'title', 'cover_image', 'genre', 'platform', 'release_date']


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    game_details = GameBasicSerializer(source='game', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'game', 'game_details', 'created_at']
        read_only_fields = ['created_at']
