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
        self.selected_entity = None  # Entity or Army
        self.hovered_entity = None
        self.selection_mode = 'normal'  # 'normal' or 'target'

    def handle_events(self):
        """Process events - main method"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            elif event.type == pygame.KEYDOWN:
                # Handle ESC
                if event.key == pygame.K_ESCAPE:
                    if self.game.waiting_for_target:
                        self.game.cancel_targeted_action()
                    else:
                        self.deselect()

                # Handle keyboard shortcuts for commands
                elif self.selected_entity and hasattr(self.game, 'actions_panel'):
                    self.game.actions_panel.handle_event(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicked on actions panel first
                if hasattr(self.game, 'actions_panel') and self.game.actions_panel.rect.collidepoint(event.pos):
                    clicked_action = self.game.actions_panel.handle_event(event)
                    if clicked_action:
                        self.game.handle_action_click(clicked_action)
                
                elif event.button == 1:  # Left click
                    self.handle_left_click(event.pos)
                elif event.button == 3:  # Right button press
                    self.right_dragging = True
                    self.last_mouse_pos = event.pos
                elif event.button == 4:  # Scroll up
                    # If mouse is over actions panel
                    if hasattr(self.game, 'actions_panel') and self.game.actions_panel.rect.collidepoint(event.pos):
                        self.game.actions_panel.handle_event(event)
                    else:
                        self.camera.zoom_in()
                elif event.button == 5:  # Scroll down
                    # If mouse is over actions panel
                    if hasattr(self.game, 'actions_panel') and self.game.actions_panel.rect.collidepoint(event.pos):
                        self.game.actions_panel.handle_event(event)
                    else:
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
                    self.update_hover(event.pos)

                # Handle mouse movement over actions panel
                if hasattr(self.game, 'actions_panel'):
                    self.game.actions_panel.handle_event(event)

    def update_hover(self, screen_pos):
        """Update which entity the mouse is hovering over"""
        # Don't update hover if mouse is over actions panel
        if hasattr(self.game, 'actions_panel') and self.game.actions_panel.rect.collidepoint(screen_pos):
            self.hovered_entity = None
            return
        
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
        """Get the clicked entity"""
        world_pos = self.camera.screen_to_world(pos)
        for entity_list in [self.game.cities, self.game.castles, 
                           self.game.checkpoints, self.game.armies]:
            for e in entity_list:
                if e.is_clicked(world_pos):
                    return e
        return None

    def handle_left_click(self, pos):
        """Handle left click"""
        world_pos = self.camera.screen_to_world(pos)

        # If we are in target selection mode (for command system)
        if self.selection_mode == 'target' and hasattr(self.game, 'complete_targeted_action'):
            self.game.complete_targeted_action(world_pos)
            return
        
        entity = self.get_clicked_entity(pos)

        # Basic functions - old system, to be removed
        # Handle army selection
        if hasattr(entity, "destination"):
            self.selected_army = entity
            self.selected_entity = entity  # Update for new system

            # Update actions panel
            if hasattr(self.game, 'actions_panel'):
                self.game.actions_panel.set_entity(entity)
            
            print(f"Selected {self.selected_army} for movement")
            return

        # If we have a selected army and the entity has a garrison
        if self.selected_army and entity and hasattr(entity, "garrison"):
            self.selected_army.sit_destination(
                (entity.x, entity.y), 
                self.game.pathfinding,
                target_entity=entity
            )
            print(f"Moving {self.selected_army} to enter {entity}")
            self.selected_army = None
            return

        # If we have a selected army, move it
        if self.selected_army:
            self.selected_army.sit_destination(world_pos, self.game.pathfinding)
            print(f"Moving {self.selected_army} to {world_pos}")
            self.selected_army = None
            return

        # Remove army from city
        # if entity and hasattr(entity, "garrison") and entity.garrison and len(entity.garrison):
        #     entity.expelling_first_army()
        #     print(f"entity garrison : {len(entity.garrison)}")

        # Identify entity and display its information
        if entity:
            self.selected_entity = entity

            # Update actions panel
            if hasattr(self.game, 'actions_panel'):
                self.game.actions_panel.set_entity(entity)
            
            print(f"Clicked on {entity}")
            return

        # If nothing was clicked, deselect
        self.deselect()
    
    def deselect(self):
        """Deselect all entities"""
        self.selected_army = None
        self.selected_entity = None
        
        if hasattr(self.game, 'actions_panel'):
            self.game.actions_panel.set_entity(None)

        print("❌ Deselect all entities")

    def handle_double_left_click(self, pos):
        """Handle double left click - can be used in the future"""
        pass