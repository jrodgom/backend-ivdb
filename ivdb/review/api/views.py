from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from review.models import Review
from game.models import Game
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
    
    def update(self, request, *args, **kwargs):
        """Permitir actualizar solo reviews propias"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"error": "No tienes permiso para editar esta reseña"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Permitir actualizar parcialmente solo reviews propias"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"error": "No tienes permiso para editar esta reseña"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Permitir eliminar solo reviews propias"""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"error": "No tienes permiso para eliminar esta reseña"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def average_rating(self, request):
        game_id = request.query_params.get('game')
        if not game_id:
            return Response({"error": "game parameter is required"}, status=400)
        avg = Review.objects.filter(game_id=game_id).aggregate(Avg('rating'))['rating__avg']
        return Response({'game_id': game_id, 'average_rating': avg})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_reviews(self, request):
        """Obtiene todas las reseñas del usuario actual"""
        reviews = Review.objects.filter(user=request.user).select_related('game').order_by('-id')
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def user_review(self, request):
        """Obtiene la review del usuario actual para un juego específico por título"""
        game_title = request.query_params.get('game_title')
        if not game_title:
            return Response({"error": "game_title parameter is required"}, status=400)
        
        try:
            # Búsqueda case-insensitive
            game = Game.objects.filter(title__iexact=game_title).first()
            if not game:
                return Response({"detail": "Game not found"}, status=status.HTTP_404_NOT_FOUND)
            
            review = Review.objects.filter(user=request.user, game=game).first()
            
            if review:
                serializer = self.get_serializer(review)
                return Response(serializer.data)
            else:
                return Response({"detail": "No review found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)