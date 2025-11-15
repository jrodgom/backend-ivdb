from rest_framework import serializers
from review.models import Review
from game.models import Game

class GameBasicSerializer(serializers.ModelSerializer):
    """Serializer simplificado para incluir en reviews"""
    class Meta:
        model = Game
        fields = ['id', 'title', 'cover_image', 'genre', 'platform']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    game_details = GameBasicSerializer(source='game', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
