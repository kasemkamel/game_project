# core/engine.py
import pygame
from core.camera import Camera
from core.renderer import Renderer
from core.game_loop import GameLoop
from core.input_manager import InputManager
from core.map_loader import MapLoader
from ui.loading_screen import LoadingScreen
from ui.actions_panel import ActionsPanel
from systems.actions_system import ActionsSystem
from entities.army import Army
from systems.pathfinding import PathfindingSystem
from ui.garrison_dialog import GarrisonSelectionDialog

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Strategic Province Engine")
        self.clock = pygame.time.Clock()

        # Initialize loading screen
        self.loading_screen = LoadingScreen(self.screen)
        self.garrison_dialog = None
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
        self.armies = [
            Army(150, 150, "north", commander="Lord A", assistant="Sir B", owner="Player"),
        ]
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

        # Initialize Actions System (93%)
        self.loading_screen.update(0.93, "Loading actions system...")
        self.loading_screen.render()
        self.actions_system = ActionsSystem()
        self._register_custom_actions()
        
        # Create Actions Panel (94%)
        self.loading_screen.update(0.94, "Creating UI panels...")
        self.loading_screen.render()
        self.actions_panel = ActionsPanel(
            x=self.WIDTH - 340,  # 10 pixels from right edge
            y=10,
            width=330,
            height=self.HEIGHT - 20
        )

        # Initialize input manager (95%)
        self.input = InputManager(self)
        self.loading_screen.update(0.95, "Initializing input manager...")
        self.loading_screen.render()

        # Register game loops (100%)
        self.loading_screen.update(1.0, "Starting game...")
        self.loading_screen.render()
        pygame.time.wait(500)
        
        self.loop.register_fast_tick(self.update_fast)
        self.loop.register_slow_tick(self.update_slow)

        self.running = True
        
        # Game state for actions
        self.waiting_for_target = False
        self.pending_action = None
        
        print("✓ Game ready! Select entity to see available actions")
        print("✓ Controls:")
        print("  - Left Click: Select/Move")
        print("  - Right Drag: Pan camera")
        print("  - Scroll: Zoom")
        print("  - ESC: Cancel/Deselect")

    def _register_custom_actions(self):
        """Register custom actions for entities."""
        from systems.actions_system import Action, ActionCategory
        
        # command: show army info
        def show_army_info(army, **kwargs):
            print(f"\n📊 information about: {army}:")
            print(f"  📍 location: ({int(army.x)}, {int(army.y)})")
            print(f"  👤 commander: {army.commander}")
            print(f"  👥 assistant: {army.assistant}")
            print(f"  🏰 status: {'in {}'.format(army.city.name) if army.city else 'in the field'}")
            print(f"  🎯 destination: {'active' if army.path else 'none'}")
            print(f"  💪 strength: {army.calculate_power()}")
            print(f"  😊 morale: {army.morale}%")
            print(f"  ⚔️ units: {len(army.units)}")

        self.actions_system.register_action("Army", Action(
            id="show_info",
            name="show army info",
            description="Display detailed information about the army",
            category=ActionCategory.MANAGEMENT,
            icon="ℹ️",
            hotkey="I",
            can_execute=lambda army: True,
            execute=show_army_info
        ))

        # command: stop army
        def stop_army(army, **kwargs):
            army.path = None
            army.destination = None
            army.target_entity = None
            print(f"⏹️ {army} stopped")
        
        self.actions_system.register_action("Army", Action(
            id="stop",
            name="stop army",
            description="Stop the army from moving",
            category=ActionCategory.MOVEMENT,
            icon="⏹️",
            hotkey="S",
            can_execute=lambda army: army.path is not None,
            execute=stop_army,
            get_tooltip=lambda army: "Stop the army from moving" if army.path else "Army is already stationary"
        ))

        # command: show city info
        def show_city_info(city, **kwargs):
            print(f"\n🏰 information about: {city.name}:")
            print(f"  📍 location: ({int(city.x)}, {int(city.y)})")
            print(f"  👑 owner: {city.owner or 'none'}")
            print(f"  🛡️ garrison: {len(city.garrison)} armies")
            if city.garrison:
                for i, army in enumerate(city.garrison, 1):
                    print(f"     {i}. {army}")
        
        self.actions_system.register_action("City", Action(
            id="show_city_info",
            name="show city info",
            description="Display detailed information about the city",
            category=ActionCategory.MANAGEMENT,
            icon="ℹ️",
            hotkey="I",
            can_execute=lambda city: True,
            execute=show_city_info
        ))

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

    def handle_action_click(self, action):
        """Handle click on an action from the panel"""
        entity = self.input.selected_entity
        
        if not entity:
            return

        print(f"\n🎯 Executing: {action.name}")

        if action.id in ['move_to', 'enter_city']:
            self.waiting_for_target = True
            self.pending_action = action
            self.input.selection_mode = 'target'
            print(f"⏳ Click on the map to set the target (ESC to cancel)")
            return
        
        if action.id == 'expel_army':
            if hasattr(entity, 'garrison') and len(entity.garrison) > 0:
                self.garrison_dialog = GarrisonSelectionDialog(
                    entity,
                    self.WIDTH,
                    self.HEIGHT
                )
                print(f"📋 Opened garrison list ({len(entity.garrison)} armies)")
            else:
                print(f"⚠️ No armies in garrison")
            return
        
        if action.id == 'view_garrison':
            if hasattr(entity, 'garrison'):
                print(f"\n📋 Garrison of {entity.name}:")
                if len(entity.garrison) > 0:
                    for i, army in enumerate(entity.garrison, 1):
                        print(f"  {i}. {army}")
                else:
                    print("  (empty)")
            return

        # Execute direct commands
        if action.id == 'expel_army':
            if hasattr(entity, 'expelling_first_army') and hasattr(entity, 'garrison'):
                if len(entity.garrison) > 0:
                    entity.expelling_first_army()
                    print(f"✓ Expelled an army from {entity.name}")
                else:
                    print(f"⚠️ No armies in garrison")

        elif action.id == 'view_garrison':
            if hasattr(entity, 'garrison'):
                print(f"\n📋 Garrison of {entity.name}:")
                if len(entity.garrison) > 0:
                    for i, army in enumerate(entity.garrison, 1):
                        print(f"  {i}. {army}")
                else:
                    print("  (empty)")

        elif action.execute:
            # Execute custom command
            action.execute(entity)

    def complete_targeted_action(self, target_pos):
        """Complete an action that requires a target selection"""
        if not self.pending_action or not self.input.selected_entity:
            return
        
        action = self.pending_action
        entity = self.input.selected_entity
        
        if action.id == 'move_to':
            if isinstance(entity, Army):
                entity.sit_destination(target_pos, self.pathfinding)
                print(f"✓ Moving {entity} to ({int(target_pos[0])}, {int(target_pos[1])})")
        
        elif action.id == 'enter_city':
            # Find a city or castle at the location
            clicked_entity = self.input.get_clicked_entity(pygame.mouse.get_pos())
            
            if clicked_entity and hasattr(clicked_entity, 'garrison'):
                if isinstance(entity, Army):
                    entity.set_destination(
                        (clicked_entity.x, clicked_entity.y),
                        self.pathfinding,
                        target_entity=clicked_entity
                    )
                    print(f"✓ {entity} heading to enter {clicked_entity.name}")
            else:
                print("⚠️ No city or castle found at this location")

        self.cancel_targeted_action()

    def cancel_targeted_action(self):
        """Cancel an action that requires a target"""
        self.waiting_for_target = False
        self.pending_action = None
        self.input.selection_mode = 'normal'
        print("❌ Action canceled")

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            # Handle input
            # If garrison dialog is open, handle its events first
            if self.garrison_dialog:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                    
                    result = self.garrison_dialog.handle_event(event)
                    
                    if result == "CANCEL":
                        print("❌ Army selection canceled")
                        self.garrison_dialog = None
                    elif result:  # An army was selected
                        # Expel the selected army
                        if hasattr(self.input.selected_entity, 'expel_specific_army'):
                            self.input.selected_entity.expel_specific_army(result)
                            print(f"✓ Expelled {result} from {self.input.selected_entity.name}")
                        self.garrison_dialog = None
            else:
                # Normal input handling
                self.input.handle_events()
            
            # Update game
            self.loop.update(dt)
            
            # Render
            self.renderer.render_image_mode(
                self.cities, 
                self.castles,
                self.checkpoints, 
                self.armies, 
                self.input.selected_army
            )
            
            # Draw actions panel (if an entity is selected)
            if self.input.selected_entity:
                self.actions_panel.draw(self.screen)
            
            # Draw target cursor (if we are waiting for a target)
            if self.waiting_for_target:
                self._draw_target_cursor()
            
            # Draw army selection window (above all)
            if self.garrison_dialog:
                self.garrison_dialog.draw(self.screen)
            
            pygame.display.flip()
        
        pygame.quit()

    def _draw_target_cursor(self):
        """Draw target selection cursor"""
        mouse_pos = pygame.mouse.get_pos()

        # Check that the mouse is not over the actions panel
        if self.actions_panel.rect.collidepoint(mouse_pos):
            return

        # Moving circle
        time_offset = pygame.time.get_ticks() % 1000
        radius = 20 + abs(time_offset - 500) / 25
        
        pygame.draw.circle(self.screen, (255, 255, 0), mouse_pos, int(radius), 2)
        pygame.draw.circle(self.screen, (255, 255, 0), mouse_pos, 5)

        # Cross lines
        pygame.draw.line(self.screen, (255, 255, 0),
                        (mouse_pos[0] - 15, mouse_pos[1]),
                        (mouse_pos[0] + 15, mouse_pos[1]), 2)
        pygame.draw.line(self.screen, (255, 255, 0), 
                        (mouse_pos[0], mouse_pos[1] - 15), 
                        (mouse_pos[0], mouse_pos[1] + 15), 2)

        # Label
        font = pygame.font.Font(None, 24)
        action_name = self.pending_action.name if self.pending_action else "Select Target"
        text = font.render(f"{action_name} (ESC to cancel)", True, (255, 255, 0))
        text_rect = text.get_rect(center=(self.WIDTH // 2, 30))
        
        # خلفية للنص
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (40, 40, 60), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 0), bg_rect, 2)
        
        self.screen.blit(text, text_rect)