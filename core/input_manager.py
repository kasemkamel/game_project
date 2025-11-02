# core/input_manager.py
import pygame

class InputManager:
    def __init__(self, game):
        self.game = game
        self.camera = game.camera
        self.screen = game.screen
        self.right_dragging = False
        self.last_mouse_pos = (0, 0)
        self.selected_army = None
        self.hovered_entity = None  # Track currently hovered entity

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_left_click(event.pos)
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

            elif event.type == pygame.MOUSEMOTION:
                if self.right_dragging:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.camera.move(-dx, -dy)
                    self.last_mouse_pos = event.pos
                else:
                    # Update hover detection
                    self.update_hover(event.pos)

    def update_hover(self, screen_pos):
        """Update which entity the mouse is hovering over"""
        world_pos = self.camera.screen_to_world(screen_pos)
        self.hovered_entity = None
        
        # Check all entity lists for hover
        for entity_list in [self.game.cities, self.game.castles, 
                           self.game.checkpoints, self.game.armies]:
            for e in entity_list:
                if e.is_clicked(world_pos):
                    self.hovered_entity = e
                    return

    def get_clicked_entity(self, pos):
        world_pos = self.camera.screen_to_world(pos)
        for entity_list in [self.game.cities, self.game.castles, 
                           self.game.checkpoints, self.game.armies]:
            for e in entity_list:
                if e.is_clicked(world_pos):
                    return e
        return None

    def handle_left_click(self, pos):
        world_pos = self.camera.screen_to_world(pos)
        entity = self.get_clicked_entity(pos)
        
        if entity and hasattr(entity, "destination"):
            self.selected_army = entity
            print(f"Selected {self.selected_army} for movement")
            return
        
        if self.selected_army and entity and hasattr(entity, "garrison"):
            self.selected_army.set_destination(
                (entity.x, entity.y), 
                self.game.pathfinding,
                target_entity=entity
            )
            print(f"Moving {self.selected_army} to enter {entity}")
            self.selected_army = None
            return

        if self.selected_army:
            self.selected_army.set_destination(world_pos, self.game.pathfinding)
            print(f"Moving {self.selected_army} to {world_pos}")
            self.selected_army = None

        if entity and hasattr(entity, "garrison") and entity.garrison and len(entity.garrison):
            entity.expelling_first_army()
            print(f"entity garrison : {len(entity.garrison)}")

        if entity:
            print(f"Clicked on {entity}")
    
    def handle_double_left_click(self, pos):
        pass