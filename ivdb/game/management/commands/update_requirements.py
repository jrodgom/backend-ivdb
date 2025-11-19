import requests
import time
from django.core.management.base import BaseCommand
from game.models import Game

RAWG_API_KEY = "3994c5d1391e4fc8b4e7eca9428d8a8b"


class Command(BaseCommand):
    help = "Actualiza los requisitos del sistema de juegos existentes desde RAWG"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limitar el número de juegos a actualizar (por defecto: todos)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Segundos de espera entre cada petición (por defecto: 0.5)'
        )

    def get_game_id_from_rawg(self, game_title):
        """Buscar el ID del juego en RAWG por su título"""
        url = "https://api.rawg.io/api/games"
        params = {
            "key": RAWG_API_KEY,
            "search": game_title,
            "page_size": 1
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    return results[0]["id"]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error buscando '{game_title}': {e}"))
        
        return None

    def get_game_requirements(self, game_id):
        """Obtiene los requisitos del sistema desde RAWG"""
        url = f"https://api.rawg.io/api/games/{game_id}"
        params = {"key": RAWG_API_KEY}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                platforms = data.get("platforms", [])
                
                # Buscar la plataforma PC
                for platform_data in platforms:
                    platform_info = platform_data.get("platform", {})
                    if platform_info.get("name") == "PC":
                        requirements = platform_data.get("requirements", {})
                        minimum = requirements.get("minimum")
                        recommended = requirements.get("recommended")
                        
                        if minimum or recommended:
                            return {
                                "minimum": minimum,
                                "recommended": recommended
                            }
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error obteniendo requisitos para ID {game_id}: {e}"))
            return None

    def handle(self, *args, **options):
        limit = options['limit']
        delay = options['delay']
        
        # Obtener juegos que no tienen requisitos y son de PC
        games = Game.objects.filter(
            minimum_requirements__isnull=True,
            recommended_requirements__isnull=True,
            platform__icontains="PC"
        )
        
        if limit:
            games = games[:limit]
        
        total_games = games.count()
        
        if total_games == 0:
            self.stdout.write(self.style.WARNING("No hay juegos de PC sin requisitos para actualizar."))
            return
        
        self.stdout.write(self.style.SUCCESS(f"🎮 Encontrados {total_games} juegos de PC para actualizar"))
        self.stdout.write(self.style.WARNING(f"⏱️  Tiempo estimado: ~{total_games * delay:.1f} segundos\n"))
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for index, game in enumerate(games, 1):
            self.stdout.write(f"[{index}/{total_games}] Procesando: {game.title}")
            
            # Buscar el ID del juego en RAWG
            game_id = self.get_game_id_from_rawg(game.title)
            
            if not game_id:
                self.stdout.write(self.style.WARNING(f"  ⏩ No se encontró en RAWG"))
                skipped_count += 1
                time.sleep(delay)
                continue
            
            # Obtener requisitos
            requirements = self.get_game_requirements(game_id)
            
            if requirements:
                game.minimum_requirements = requirements["minimum"]
                game.recommended_requirements = requirements["recommended"]
                game.save()
                
                req_types = []
                if requirements["minimum"]:
                    req_types.append("mínimos")
                if requirements["recommended"]:
                    req_types.append("recomendados")
                
                self.stdout.write(self.style.SUCCESS(f"  ✅ Actualizado con requisitos {' y '.join(req_types)}"))
                updated_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  No tiene requisitos de PC en RAWG"))
                skipped_count += 1
            
            # Esperar entre peticiones para no saturar la API
            time.sleep(delay)
        
        # Resumen final
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"✅ Actualizados: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"⏩ Omitidos: {skipped_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"❌ Errores: {error_count}"))
        self.stdout.write("="*50)
