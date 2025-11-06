from rest_framework import serializers
from review.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    game = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
