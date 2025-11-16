from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from favorite.models import Favorite
from .serializers import FavoriteSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Obtener solo los favoritos del usuario actual"""
        return Favorite.objects.filter(user=self.request.user).select_related('game')

    def perform_create(self, serializer):
        """Crear favorito para el usuario actual"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create para manejar duplicados"""
        game_id = request.data.get('game')
        
        if not game_id:
            return Response(
                {"error": "Se requiere el ID del juego"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya existe
        if Favorite.objects.filter(user=request.user, game_id=game_id).exists():
            return Response(
                {"error": "Este juego ya está en tus favoritos"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Permitir eliminar solo favoritos propios"""
        favorite = self.get_object()
        if favorite.user != request.user:
            return Response(
                {"error": "No tienes permiso para eliminar este favorito"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle favorito - si existe lo elimina, si no existe lo crea"""
        game_id = request.data.get('game_id')
        
        if not game_id:
            return Response(
                {"error": "Se requiere game_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            favorite = Favorite.objects.get(user=request.user, game_id=game_id)
            favorite.delete()
            return Response(
                {"message": "Juego eliminado de favoritos", "is_favorite": False},
                status=status.HTTP_200_OK
            )
        except Favorite.DoesNotExist:
            favorite = Favorite.objects.create(user=request.user, game_id=game_id)
            serializer = self.get_serializer(favorite)
            return Response(
                {"message": "Juego añadido a favoritos", "is_favorite": True, "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

    @action(detail=False, methods=['get'])
    def check(self, request):
        """Verificar si un juego es favorito del usuario"""
        game_id = request.query_params.get('game_id')
        
        if not game_id:
            return Response(
                {"error": "Se requiere game_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_favorite = Favorite.objects.filter(user=request.user, game_id=game_id).exists()
        return Response({"is_favorite": is_favorite})
