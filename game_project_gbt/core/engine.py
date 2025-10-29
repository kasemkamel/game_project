# core/engine.py
import pygame
from core.camera import Camera
from core.renderer import Renderer
from core.game_loop import GameLoop
from core.input_manager import InputManager
from entities.city import City
from entities.castle import Castle
from entities.checkpoint import Checkpoint
from entities.province import Province
from entities.army import Army

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Strategic Province Engine")
        self.clock = pygame.time.Clock()

        # Core systems
        self.camera = Camera(self.WIDTH, self.HEIGHT)
        self.renderer = Renderer(self.screen, self.camera)
        self.input = InputManager(self)
        self.loop = GameLoop()

        # Entities
        self.provinces, self.cities, self.castles, self.checkpoints, self.armies = self.create_entities()

        # Tick handlers
        self.loop.register_fast_tick(self.update_fast)
        self.loop.register_slow_tick(self.update_slow)

        self.running = True

    def create_entities(self):
        provinces = [
            Province([(100, 100), (400, 120), (350, 400), (150, 350)], (120, 200, 120)),
            Province([(500, 200), (800, 250), (750, 550), (500, 500)], (100, 180, 220))
        ]
        cities = [City(250, 250, "Greenfield"), City(650, 350, "Rivergate")]
        castles = [Castle(200, 300), Castle(700, 450)]
        checkpoints = [Checkpoint(400, 300), Checkpoint(550, 400)]
        armies = [Army(500, 400)]
        return provinces, cities, castles, checkpoints, armies

    def update_fast(self, dt):
        """Fast tick: runs every 1/20 sec"""
        for army in self.armies:
            army.update(dt)

    def update_slow(self):
        """Slow tick: runs every 4 minutes"""
        print("[SLOW TICK] Running resource + happiness systems")

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # frame delta (s)
            self.input.handle_events()
            self.loop.update(dt)
            self.renderer.render(self.provinces, self.cities, self.castles, self.checkpoints, self.armies)
            pygame.display.flip()
        pygame.quit()
