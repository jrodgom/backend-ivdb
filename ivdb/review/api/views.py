from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from review.models import Review
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        game_id = self.request.query_params.get('game')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def average_rating(self, request):
        game_id = request.query_params.get('game')
        if not game_id:
            return Response({"error": "game parameter is required"}, status=400)
        avg = Review.objects.filter(game_id=game_id).aggregate(Avg('rating'))['rating__avg']
        return Response({'game_id': game_id, 'average_rating': avg})