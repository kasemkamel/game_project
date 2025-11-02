# core/engine.py
import pygame
from core.camera import Camera
from core.renderer import Renderer
from core.game_loop import GameLoop
from core.input_manager import InputManager
from core.map_loader import MapLoader
from ui.loading_screen import LoadingScreen
from entities.army import Army
from systems.pathfinding import PathfindingSystem

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Strategic Province Engine")
        self.clock = pygame.time.Clock()

        # Initialize loading screen
        self.loading_screen = LoadingScreen(self.screen)
        
        # Initialize core systems with loading updates
        self._initialize_game()

    def _initialize_game(self):
        """Initialize game with loading screen updates"""
        
        # Camera (5%)
        self.loading_screen.update(0.05, "Initializing camera...")
        self.loading_screen.render()
        self.camera = Camera(self.WIDTH, self.HEIGHT)
        
        # Core systems (12%)
        self.loading_screen.update(0.12, "Loading core systems...")
        self.loading_screen.render()
        self.renderer = Renderer(self, self.screen, self.camera)
        self.loop = GameLoop()
        
        # Load map (40%)
        self.loading_screen.update(0.37, "Loading map data...")
        self.loading_screen.render()
        print("Loading map data...")
        self.map_loader = MapLoader("assets/maps/map_model_v8.geojson")
        
        if not self.map_loader.load_map():
            print("Failed to load map! Using fallback entities.")
            self.provinces, self.cities, self.castles, self.checkpoints, self.mountains, self.rivers = self.create_fallback_entities()
        else:
            self.provinces, self.cities, self.castles, self.checkpoints, self.mountains, self.rivers = self.map_loader.get_all_entities()
        
        print(f"✓ Game initialized with {len(self.provinces)} provinces")
        print(f"✓ Obstacles: {len(self.mountains)} mountains, {len(self.rivers)} rivers")
        
        # Create armies (47%)
        self.loading_screen.update(0.47, "Creating armies...")
        self.loading_screen.render()
        self.armies = [Army(500, 400)]
        self.obstacles = self.mountains + self.rivers
        
        # Initialize pathfinding (57-92%)
        self.loading_screen.update(0.57, "Building pathfinding system...")
        self.loading_screen.render()
        print(f"Initializing pathfinding system with {len(self.obstacles)} obstacles...")
        print("Building visibility graph (this may take 5-10 seconds)...")
        
        self.pathfinding = PathfindingSystem(
            self,
            obstacles=[t.polygon for t in self.obstacles],
            max_vertices_per_poly=25,
            simplify_tolerance=3.0,
            max_edge_length=None,
            cache_graph=True,
            smoothing_iterations=2,
            debug_mode=False,
            use_buffer=True
        )
        
        self.loading_screen.update(0.92, "Finalizing pathfinding...")
        self.loading_screen.render()
        
        stats = self.pathfinding.get_stats()
        print(f"✓ Pathfinding ready:")
        print(f"  - Total vertices: {stats['total_vertices']}")
        print(f"  - Cached nodes: {stats.get('cached_nodes', 'N/A')}")
        print(f"  - Cached edges: {stats.get('cached_edges', 'N/A')}")

        # Initialize input manager (95%)
        self.input = InputManager(self)
        self.loading_screen.update(0.95, "Initializing input manager...")
        self.loading_screen.render()

        # Register game loops (100%)
        self.loading_screen.update(1.0, "Starting game...")
        self.loading_screen.render()
        pygame.time.wait(500)  # Brief pause to show 100%
        
        self.loop.register_fast_tick(self.update_fast)
        self.loop.register_slow_tick(self.update_slow)

        self.running = True
        print("✓ Game ready! Click to select army, click again to move")

    def create_fallback_entities(self):
        """Fallback entities if map loading fails."""
        from entities.province import Province
        from entities.city import City
        from entities.castle import Castle
        from entities.checkpoint import Checkpoint
        from entities.terrain import terrain
        
        provinces = [
            Province([(100, 100), (400, 120), (350, 400), (150, 350)], (120, 200, 120)),
            Province([(500, 200), (800, 250), (750, 550), (500, 500)], (100, 180, 220))
        ]
        cities = [City(250, 250, "Greenfield"), City(650, 350, "Rivergate")]
        castles = [Castle(200, 300), Castle(700, 450)]
        checkpoints = [Checkpoint(400, 300), Checkpoint(550, 400)]
        mountains = [
            terrain([(300, 150), (400, 140), (450, 200), (400, 250), (300, 240)], (139, 137, 137))
        ]
        rivers = []
        return provinces, cities, castles, checkpoints, mountains, rivers

    def update_fast(self, dt):
        """Fast tick: runs frequently"""
        for army in self.armies:
            army.update(dt)

    def update_slow(self):
        """Slow tick: runs every 4 minutes"""
        print("[SLOW TICK] Running resource + happiness systems")

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.input.handle_events()
            self.loop.update(dt)
            self.renderer.render_image_mode(
                self.cities, 
                self.castles,
                self.checkpoints, 
                self.armies, 
                self.input.selected_army
            )
            pygame.display.flip()
        pygame.quit()