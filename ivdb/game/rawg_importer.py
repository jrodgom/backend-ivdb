import requests
from .models import Game

RAWG_API_URL = "https://api.rawg.io/api/games"
RAWG_API_KEY = "3994c5d1391e4fc8b4e7eca9428d8a8b"  # ⚠️ No subir a GitHub


def get_game_requirements(game_id):
    """
    Obtiene los requisitos del sistema de un juego desde RAWG.
    Retorna un diccionario con requisitos mínimos y recomendados para PC.
    """
    url = f"https://api.rawg.io/api/games/{game_id}"
    params = {"key": RAWG_API_KEY}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            platforms = data.get("platforms", [])
            
            # Buscar la plataforma PC y sus requisitos
            for platform_data in platforms:
                platform_info = platform_data.get("platform", {})
                if platform_info.get("name") == "PC":
                    requirements = platform_data.get("requirements", {})
                    return {
                        "minimum": requirements.get("minimum"),
                        "recommended": requirements.get("recommended")
                    }
        return None
    except Exception as e:
        print(f"Error obteniendo requisitos: {e}")
        return None


def import_games_from_rawg(pages=10, page_size=100):
    """
    Importa juegos desde RAWG y los guarda en la base de datos.
    Por defecto trae 1000 juegos (10 páginas x 100 por página).
    """

    for page in range(1, pages + 1):
        params = {
            "key": RAWG_API_KEY,
            "page": page,
            "page_size": page_size,
        }

        response = requests.get(RAWG_API_URL, params=params)

        if response.status_code != 200:
            print(f"❌ Error al conectar con RAWG (página {page}):", response.status_code)
            break

        data = response.json()
        results = data.get("results", [])

        print(f"📦 Página {page} - {len(results)} juegos encontrados")

        for game_data in results:
            game_id = game_data["id"]
            title = game_data["name"]
            cover_image = game_data.get("background_image", "")
            release_date = game_data.get("released")
            genre = ", ".join([g["name"] for g in game_data.get("genres", [])])
            platform = ", ".join(
                [p["platform"]["name"] for p in game_data.get("platforms", [])]
            )
            metacritic = game_data.get("metacritic")  # Obtener puntuación de Metacritic
            rating = game_data.get("rating")  # Obtener rating de RAWG (0-5)
            
            # Obtener requisitos del sistema si es un juego de PC
            requirements = None
            if "PC" in platform:
                requirements = get_game_requirements(game_id)

            # Evita duplicados
            if not Game.objects.filter(title=title).exists():
                Game.objects.create(
                    title=title,
                    description="Importado desde RAWG",
                    release_date=release_date if release_date else None,
                    genre=genre,
                    platform=platform,
                    developer="",
                    cover_image=cover_image,
                    metacritic=metacritic,
                    rating=rating,
                    minimum_requirements=requirements.get("minimum") if requirements else None,
                    recommended_requirements=requirements.get("recommended") if requirements else None,
                )
                print(f"✅ Añadido: {title}")
            else:
                print(f"⏩ Ya existía: {title}")
