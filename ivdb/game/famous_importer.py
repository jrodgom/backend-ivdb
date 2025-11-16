import requests
from .models import Game

RAWG_API_URL = "https://api.rawg.io/api/games"
RAWG_API_KEY = "3994c5d1391e4fc8b4e7eca9428d8a8b"


def import_famous_games():
    """
    Importa los juegos MÁS FAMOSOS y reconocibles.
    GTA, Red Dead, Minecraft, Cyberpunk, Witcher, etc.
    """
    
    # Lista de juegos ultra-famosos que TODOS conocen
    famous_games = [
        # Rockstar Games
        "Grand Theft Auto V",
        "Grand Theft Auto IV",
        "Grand Theft Auto: San Andreas",
        "Grand Theft Auto: Vice City",
        "Red Dead Redemption 2",
        "Red Dead Redemption",
        
        # CD Projekt Red
        "The Witcher 3: Wild Hunt",
        "Cyberpunk 2077",
        "The Witcher 2: Assassins of Kings",
        
        # Mojang/Microsoft
        "Minecraft",
        
        # Valve
        "Counter-Strike: Global Offensive",
        "Portal 2",
        "Half-Life 2",
        "Left 4 Dead 2",
        "Team Fortress 2",
        
        # Bethesda
        "The Elder Scrolls V: Skyrim",
        "Fallout 4",
        "Fallout: New Vegas",
        "Doom",
        "Doom Eternal",
        
        # Ubisoft
        "Assassin's Creed II",
        "Assassin's Creed IV: Black Flag",
        "Far Cry 3",
        "Rainbow Six Siege",
        "Watch Dogs",
        
        # EA
        "The Sims 4",
        "Battlefield 1",
        "Battlefield 4",
        "FIFA 23",
        "Need for Speed: Most Wanted",
        "Mass Effect 2",
        
        # Sony
        "God of War",
        "The Last of Us",
        "Horizon Zero Dawn",
        "Spider-Man",
        "Uncharted 4: A Thief's End",
        
        # Nintendo
        "The Legend of Zelda: Breath of the Wild",
        "Super Mario Odyssey",
        
        # Otros AAA famosos
        "Call of Duty: Modern Warfare",
        "Call of Duty: Black Ops",
        "Fortnite",
        "Overwatch",
        "League of Legends",
        "Dota 2",
        "Resident Evil 4",
        "Dark Souls III",
        "Sekiro: Shadows Die Twice",
        "Elden Ring",
        "Halo: The Master Chief Collection",
        "Apex Legends",
        "Valorant",
        "Among Us",
        "Fall Guys",
        "Rocket League",
        "Stardew Valley",
        "Terraria",
        "Hollow Knight",
        "Celeste",
        "Dead Cells",
        "Hades",
        "Undertale",
        "Cuphead",
        "Bioshock Infinite",
        "Borderlands 2",
        "Monster Hunter: World",
        "Final Fantasy XV",
        "Persona 5",
        "Metal Gear Solid V",
        "Death Stranding",
        "Days Gone",
        "Ghost of Tsushima",
        "Bloodborne",
        "Minecraft Dungeons",
        "Sea of Thieves",
        "State of Decay 2",
        "Gears 5",
        "Forza Horizon 5",
        "Forza Horizon 4",
        "F1 2021",
        "NBA 2K21",
        "Control",
        "Star Wars Jedi: Fallen Order",
        "Star Wars Battlefront II",
    ]
    
    imported_count = 0
    
    print("🌟 Importando juegos ULTRA-FAMOSOS...")
    print(f"Total de juegos a buscar: {len(famous_games)}\n")
    
    for game_title in famous_games:
        try:
            # Buscar el juego exacto en RAWG
            params = {
                "key": RAWG_API_KEY,
                "search": game_title,
                "page_size": 3,
            }
            
            response = requests.get(RAWG_API_URL, params=params)
            
            if response.status_code != 200:
                print(f"❌ Error buscando '{game_title}'")
                continue
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                print(f"⚠️ No encontrado: {game_title}")
                continue
            
            # Tomar el primer resultado (más relevante)
            game_data = results[0]
            title = game_data["name"]
            
            # Evitar duplicados
            if Game.objects.filter(title=title).exists():
                print(f"⏩ Ya existe: {title}")
                continue
            
            # Crear juego
            Game.objects.create(
                title=title,
                description=game_data.get("description_raw", "") or f"Juego famoso: {title}",
                release_date=game_data.get("released"),
                genre=", ".join([g["name"] for g in game_data.get("genres", [])[:3]]),
                platform=", ".join([p["platform"]["name"] for p in game_data.get("platforms", [])[:5]]),
                developer="",
                cover_image=game_data.get("background_image", ""),
                metacritic=game_data.get("metacritic"),
                rating=game_data.get("rating"),
            )
            
            imported_count += 1
            print(f"✅ [{imported_count}] {title} (Metacritic: {game_data.get('metacritic', 'N/A')})")
            
        except Exception as e:
            print(f"❌ Error con '{game_title}': {str(e)}")
            continue
    
    print(f"\n🎉 Importación completada: {imported_count} juegos famosos añadidos")
    return imported_count


def import_blockbuster_games(max_games=100):
    """
    Importa juegos BLOCKBUSTER ordenados por popularidad real (added).
    Esto trae los juegos que más gente tiene/juega.
    """
    
    imported_count = 0
    page = 1
    
    print("🎬 Importando juegos BLOCKBUSTER (más populares)...")
    
    while imported_count < max_games:
        params = {
            "key": RAWG_API_KEY,
            "page": page,
            "page_size": 40,
            "ordering": "-added,-rating",  # Ordenar por popularidad (cuánta gente lo ha añadido)
            "metacritic": "75,100",  # Solo buenos
        }

        try:
            response = requests.get(RAWG_API_URL, params=params)
            
            if response.status_code != 200:
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
                    description=game_data.get("description_raw", "") or "Juego popular",
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

    print(f"\n🎉 {imported_count} juegos blockbuster importados")
    return imported_count
