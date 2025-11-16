from django.core.management.base import BaseCommand
from game.improved_importer import import_popular_games, import_games_by_genre, clear_all_games
from game.famous_importer import import_famous_games, import_blockbuster_games


class Command(BaseCommand):
    help = 'Gestiona la importación de juegos desde RAWG'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            help='Acción a realizar: famous, blockbuster, popular, genre, clear'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=200,
            help='Número de juegos a importar (default: 200)'
        )
        parser.add_argument(
            '--genre',
            type=str,
            help='Género para importar (action, adventure, role-playing-games-rpg, etc.)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'famous':
            self.stdout.write(self.style.SUCCESS('Importando juegos ULTRA-FAMOSOS...'))
            imported = import_famous_games()
            self.stdout.write(self.style.SUCCESS(f'✅ {imported} juegos famosos importados'))
            
        elif action == 'blockbuster':
            count = options['count']
            self.stdout.write(self.style.SUCCESS(f'Importando {count} juegos BLOCKBUSTER...'))
            imported = import_blockbuster_games(max_games=count)
            self.stdout.write(self.style.SUCCESS(f'✅ {imported} juegos importados'))
            
        elif action == 'popular':
            count = options['count']
            self.stdout.write(self.style.SUCCESS(f'Importando {count} juegos populares...'))
            imported = import_popular_games(max_games=count)
            self.stdout.write(self.style.SUCCESS(f'✅ {imported} juegos importados'))
            
        elif action == 'genre':
            genre = options.get('genre')
            if not genre:
                self.stdout.write(self.style.ERROR('❌ Debes especificar --genre'))
                return
            count = options['count']
            self.stdout.write(self.style.SUCCESS(f'Importando {count} juegos de {genre}...'))
            imported = import_games_by_genre(genre, max_games=count)
            self.stdout.write(self.style.SUCCESS(f'✅ {imported} juegos importados'))
            
        elif action == 'clear':
            confirm = input('⚠️ ¿Estás seguro de eliminar TODOS los juegos? (yes/no): ')
            if confirm.lower() == 'yes':
                clear_all_games()
                self.stdout.write(self.style.SUCCESS('✅ Todos los juegos eliminados'))
            else:
                self.stdout.write(self.style.WARNING('❌ Operación cancelada'))
                
        else:
            self.stdout.write(self.style.ERROR(f'❌ Acción desconocida: {action}'))
            self.stdout.write('Acciones disponibles: famous, blockbuster, popular, genre, clear')
