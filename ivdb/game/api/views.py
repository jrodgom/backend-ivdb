from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from game.models import Game
from game.api.serializers import GameSerializer
from game.filters import GameFilter
from game.rawg_importer import get_game_requirements
import requests

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

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_from_rawg(self, request):
        """
        Importa un juego desde RAWG con todos sus datos incluyendo requisitos del sistema
        """
        rawg_id = request.data.get('rawg_id')
        
        if not rawg_id:
            return Response(
                {"error": "Se requiere rawg_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        RAWG_API_KEY = "3994c5d1391e4fc8b4e7eca9428d8a8b"
        
        try:
            # Obtener detalles del juego desde RAWG
            url = f"https://api.rawg.io/api/games/{rawg_id}"
            params = {"key": RAWG_API_KEY}
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                return Response(
                    {"error": "No se pudo obtener el juego desde RAWG"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            game_data = response.json()
            
            # Verificar si el juego ya existe
            existing_game = Game.objects.filter(title=game_data["name"]).first()
            if existing_game:
                return Response(
                    {"error": "Este juego ya existe en la base de datos", "game_id": existing_game.id},
                    status=status.HTTP_409_CONFLICT
                )
            
            # Obtener requisitos del sistema
            requirements = get_game_requirements(rawg_id)
            
            # Crear el juego con toda la información
            game = Game.objects.create(
                title=game_data["name"],
                description=game_data.get("description_raw") or game_data.get("description", ""),
                release_date=game_data.get("released"),
                genre=", ".join([g["name"] for g in game_data.get("genres", [])]),
                platform=", ".join([p["platform"]["name"] for p in game_data.get("platforms", [])]),
                developer=", ".join([d["name"] for d in game_data.get("developers", [])]),
                cover_image=game_data.get("background_image", ""),
                metacritic=game_data.get("metacritic"),
                rating=game_data.get("rating"),
                minimum_requirements=requirements["minimum"] if requirements else None,
                recommended_requirements=requirements["recommended"] if requirements else None,
            )
            
            serializer = self.get_serializer(game)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Error al importar el juego: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

