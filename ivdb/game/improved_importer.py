import requests
from .models import Game

RAWG_API_URL = "https://api.rawg.io/api/games"
RAWG_API_KEY = "3994c5d1391e4fc8b4e7eca9428d8a8b"


def import_popular_games(max_games=200):
    """
    Importa juegos POPULARES desde RAWG ordenados por:
    - Metacritic score (crítica profesional)
    - Rating de usuarios
    - Juegos con muchas reseñas (added)
    
    Esto asegura que se importen juegos conocidos y de calidad.
    """
    
    imported_count = 0
    page = 1
    
    print("🎮 Iniciando importación de juegos populares...")
    
    while imported_count < max_games:
        params = {
            "key": RAWG_API_KEY,
            "page": page,
            "page_size": 40,
            "ordering": "-metacritic,-added",  # Ordenar por Metacritic y popularidad
            "metacritic": "70,100",  # Solo juegos con Metacritic >= 70
        }

        try:
            response = requests.get(RAWG_API_URL, params=params)
            
            if response.status_code != 200:
                print(f"❌ Error en página {page}: {response.status_code}")
                break

            data = response.json()
            results = data.get("results", [])
            
            if not results:
                print("⚠️ No hay más juegos disponibles")
                break

            print(f"\n📦 Página {page} - Procesando {len(results)} juegos...")

            for game_data in results:
                if imported_count >= max_games:
                    break
                    
                title = game_data["name"]
                cover_image = game_data.get("background_image", "")
                release_date = game_data.get("released")
                metacritic = game_data.get("metacritic")
                rating = game_data.get("rating")
                
                # Solo importar si tiene buena puntuación
                if not metacritic or metacritic < 70:
                    continue
                
                # Obtener géneros
                genres = game_data.get("genres", [])
                genre = ", ".join([g["name"] for g in genres[:3]]) if genres else "Unknown"
                
                # Obtener plataformas (las más importantes)
                platforms = game_data.get("platforms", [])
                platform_names = []
                for p in platforms[:5]:  # Limitar a 5 plataformas
                    platform_names.append(p["platform"]["name"])
                platform = ", ".join(platform_names) if platform_names else "Unknown"

                # Evitar duplicados
                if Game.objects.filter(title=title).exists():
                    print(f"⏩ Ya existe: {title}")
                    continue

                Game.objects.create(
                    title=title,
                    description=f"Juego popular importado desde RAWG. Metacritic: {metacritic}",
                    release_date=release_date if release_date else None,
                    genre=genre,
                    platform=platform,
                    developer="",
                    cover_image=cover_image,
                    metacritic=metacritic,
                    rating=rating,
                )
                
                imported_count += 1
                print(f"✅ [{imported_count}/{max_games}] Añadido: {title} (Metacritic: {metacritic})")

            page += 1

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            break

    print(f"\n🎉 Importación completada: {imported_count} juegos añadidos")
    return imported_count


def import_games_by_genre(genre_name, max_games=50):
    """
    Importa juegos populares de un género específico.
    
    Géneros disponibles:
    - action (Acción)
    - adventure (Aventura)
    - role-playing-games-rpg (RPG)
    - shooter (Disparos)
    - strategy (Estrategia)
    - sports (Deportes)
    - racing (Carreras)
    - indie (Indie)
    """
    
    imported_count = 0
    page = 1
    
    print(f"🎮 Importando juegos de {genre_name}...")
    
    while imported_count < max_games:
        params = {
            "key": RAWG_API_KEY,
            "page": page,
            "page_size": 40,
            "genres": genre_name,
            "ordering": "-rating,-added",
            "metacritic": "60,100",  # Juegos decentes
        }

        try:
            response = requests.get(RAWG_API_URL, params=params)
            
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code}")
                break

            data = response.json()
            results = data.get("results", [])
            
            if not results:
                break

            for game_data in results:
                if imported_count >= max_games:
                    break
                    
                title = game_data["name"]
                
                if Game.objects.filter(title=title).exists():
                    continue

                Game.objects.create(
                    title=title,
                    description=f"Juego de {genre_name} importado desde RAWG",
                    release_date=game_data.get("released"),
                    genre=", ".join([g["name"] for g in game_data.get("genres", [])[:3]]),
                    platform=", ".join([p["platform"]["name"] for p in game_data.get("platforms", [])[:5]]),
                    developer="",
                    cover_image=game_data.get("background_image", ""),
                    metacritic=game_data.get("metacritic"),
                    rating=game_data.get("rating"),
                )
                
                imported_count += 1
                print(f"✅ [{imported_count}/{max_games}] {title}")

            page += 1

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            break

    print(f"✅ {imported_count} juegos de {genre_name} importados")
    return imported_count


def clear_all_games():
    """
    Elimina TODOS los juegos de la base de datos.
    ⚠️ USAR CON PRECAUCIÓN
    """
    count = Game.objects.count()
    Game.objects.all().delete()
    print(f"🗑️ {count} juegos eliminados de la base de datos")
