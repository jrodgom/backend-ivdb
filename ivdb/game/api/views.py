from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from game.models import Game
from game.api.serializers import GameSerializer
from game.filters import GameFilter

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GameFilter
    search_fields = ['title', 'genre', 'platform', 'developer']
    ordering_fields = ['title', 'release_date', 'created_at', 'metacritic', 'rating']
    ordering = ['-metacritic', '-rating', '-created_at']

    def perform_create(self, serializer):
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para editar juegos. Solo administradores."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para editar juegos. Solo administradores."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "No tienes permisos para eliminar juegos. Solo administradores."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
