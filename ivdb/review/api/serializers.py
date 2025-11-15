from rest_framework import serializers
from review.models import Review
from game.models import Game

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())

    class Meta:
        model = Review
        fields = '__all__'
