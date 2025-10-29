# core/input_manager.py
import pygame

class InputManager:
    def __init__(self, game):
        self.game = game
        self.camera = game.camera
        self.right_dragging = False
        self.last_mouse_pos = (0, 0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    entity = self.get_clicked_entity(event.pos)
                    if entity:
                        print(f"Clicked on {entity}")
                elif event.button == 3:  # Right button press
                    self.right_dragging = True
                    self.last_mouse_pos = event.pos
                elif event.button == 4:
                    self.camera.zoom_in()
                elif event.button == 5:
                    self.camera.zoom_out()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    self.right_dragging = False

            elif event.type == pygame.MOUSEMOTION and self.right_dragging:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.camera.move(-dx, -dy)
                self.last_mouse_pos = event.pos

    def get_clicked_entity(self, pos):
        world_pos = self.camera.screen_to_world(pos)
        for entity_list in [self.game.cities, self.game.castles, self.game.checkpoints, self.game.armies]:
            for e in entity_list:
                if e.is_clicked(world_pos):
                    return e
        return None
