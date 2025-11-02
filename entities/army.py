# entities/army.py
import math
import pygame
from entities.base_entity import BaseEntity

class Army(BaseEntity):
    RADIUS = 8
    SPEED = 80
    
    def __init__(self, x, y, owner=None):
        super().__init__(x, y)
        self.destination = None
        self.path = None
        self.current_waypoint = 0
        self.owner = owner
        self.is_visible = True
        self.city = None
    
    def update(self, dt):
        """Update army position - follows computed path"""
        if not self.path or len(self.path) == 0:
            return
        
        # Check if reached end of path
        if self.current_waypoint >= len(self.path):
            if hasattr(self, 'target_entity') and self.target_entity:
                self.enter_entity(self.target_entity)
            self.path = None
            self.current_waypoint = 0
            self.target_entity = None
            return
        
        # Move toward current waypoint
        target = self.path[self.current_waypoint]
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Reached waypoint, move to next
        if distance < 5:
            self.current_waypoint += 1
            return
        
        # Move toward waypoint
        nx = dx / distance
        ny = dy / distance
        self.x += nx * self.SPEED * dt
        self.y += ny * self.SPEED * dt
        if hasattr(self, 'target_entity') and self.target_entity:
            dest_2_power = (self.x - self.target_entity.x)**2 + (self.y - self.target_entity.y)**2
            if dest_2_power < 15**2:
                self.enter_entity(self.target_entity)
    
    def set_destination(self, dest, pathfinding_system, target_entity = None):
        """Set new destination and calculate path"""
        if not pathfinding_system:
            print("[Army] No pathfinding system available!")
            return

        start = (self.x, self.y)
        
        # NEW: Handle PathfindingResult object
        result = pathfinding_system.find_path(start, dest)
        
        if result.success:
            self.path = result.path
            self.current_waypoint = 0
            self.target_entity = target_entity
            print(f"[Army] Path found: {len(result.path)} waypoints, distance: {result.distance:.1f}")
        else:
            print(f"[Army] No path found from {start} to {dest}")
            self.path = None
    
    def draw(self, screen, camera, is_selected=False):
        """Draw army and path"""
        if self.is_visible:
            pos = camera.apply((self.x, self.y))
            radius = int(self.RADIUS * camera.zoom)
            
            # Draw army
            pygame.draw.circle(screen, (255, 255, 255), pos, radius)
            pygame.draw.circle(screen, (100, 100, 100), pos, radius, 1)
            
            # Highlight if selected
            if is_selected:
                pygame.draw.circle(screen, (0, 255, 255), pos, radius + 4, 3)
        
    def enter_entity(self, entity):
        """Enter a city, castle, or checkpoint"""
        if hasattr(entity, "garrison"):
            # It's a city or castle with garrison
            entity.garrison.add(self)
            self.city = entity
            print(f"[Army] Entered {entity}, garrison size: {len(entity.garrison)}")
            # Hide the army (or remove from game.armies list)
            self.is_visible = False
        elif hasattr(entity, "activate"):
            # It's a checkpoint or special location
            entity.activate(self)
            print(f"[Army] Reached {entity}")


    def is_clicked(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx*dx + dy*dy <= self.RADIUS**2
    