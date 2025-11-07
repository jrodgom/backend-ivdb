import requests
from .models import Game

RAWG_API_URL = "https://api.rawg.io/api/games"
RAWG_API_KEY = "3994c5d1391e4fc8b4e7eca9428d8a8b"  # ⚠️ No subir a GitHub


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
            title = game_data["name"]
            cover_image = game_data.get("background_image", "")
            release_date = game_data.get("released")
            genre = ", ".join([g["name"] for g in game_data.get("genres", [])])
            platform = ", ".join(
                [p["platform"]["name"] for p in game_data.get("platforms", [])]
            )

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
                )
                print(f"✅ Añadido: {title}")
            else:
                print(f"⏩ Ya existía: {title}")
