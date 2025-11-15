from rest_framework import viewsets, permissions, filters
from game.models import Game
from game.api.serializers import GameSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all().order_by('id')
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'genre', 'platform']

    def perform_create(self, serializer):
        serializer.save()
