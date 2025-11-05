# entities/army.py
import math
import pygame
from entities.base_entity import BaseEntity

class Army(BaseEntity):
    RADIUS = 8
    BASE_SPEED = 80

    def __init__(self, x, y, commander="commander", assistant="assistant", owner=None):
        super().__init__(x, y)
        self.commander = commander
        self.assistant = assistant
        self.units = []
        self.destination = None
        self.path = None
        self.current_waypoint = 0
        self.owner = owner
        self.is_visible = True
        self.city = None
        self.morale = 100
        self.experience = 0

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
        self.x += nx * self.BASE_SPEED * dt
        self.y += ny * self.BASE_SPEED * dt
        
        if hasattr(self, 'target_entity') and self.target_entity:
            dest_2_power = (self.x - self.target_entity.x)**2 + (self.y - self.target_entity.y)**2
            if dest_2_power < 15**2:
                self.enter_entity(self.target_entity)
    
    def sit_destination(self, dest, pathfinding_system, target_entity=None):
        """Set army destination and compute path"""
        if not pathfinding_system:
            print("[Army] No pathfinding system available!")
            return

        start = (self.x, self.y)
        
        result = pathfinding_system.find_path(start, dest)
        
        if result.success:
            self.path = result.path
            self.current_waypoint = 0
            self.target_entity = target_entity
            self.destination = dest
            print(f"[Army] Path found: {len(result.path)} waypoints, distance: {result.distance:.1f}")
        else:
            print(f"[Army] No path found from {start} to {dest}")
            self.path = None
    
    def draw(self, screen, camera, is_selected=False):
        """Draw army and path"""
        if not self.is_visible:
            return
        
        pos = camera.apply((self.x, self.y))
        radius = int(self.RADIUS * camera.zoom)

        # # Draw path first
        # if self.path and len(self.path) > 1:
        #     path_points = [camera.apply(p) for p in self.path]
        #     pygame.draw.lines(screen, (100, 150, 255), False, path_points, 2)

        #     # Draw destination point
        #     if self.destination:
        #         dest_pos = camera.apply(self.destination)
        #         pygame.draw.circle(screen, (255, 255, 0), dest_pos, 5)
        #         pygame.draw.circle(screen, (255, 255, 0), dest_pos, 10, 2)

        # Draw army circle
        pygame.draw.circle(screen, (200, 50, 50), pos, radius)
        pygame.draw.circle(screen, (255, 100, 100), pos, radius, 2)

        # Selection indicator
        if is_selected:
            # Pulsating circle
            time_offset = pygame.time.get_ticks() % 1500
            selection_radius = radius + 8 + abs(time_offset - 750) / 150
            pygame.draw.circle(screen, (255, 255, 0), pos, int(selection_radius), 3)
            # Marker above army
            pygame.draw.circle(screen, (255, 255, 0), (pos[0], pos[1] - radius - 8), 3)
    
    def enter_entity(self, entity):
        """Enter a city, castle, or checkpoint"""
        if hasattr(entity, "garrison"):
            # Add to garrison
            entity.garrison.add(self)
            self.city = entity
            print(f"[Army] Entered {entity}, garrison size: {len(entity.garrison)}")
            # Hide army
            self.is_visible = False
            self.path = None
            self.destination = None
        elif hasattr(entity, "activate"):
            # Checkpoint or special location
            entity.activate(self)
            print(f"[Army] Reached {entity}")

    def is_clicked(self, pos):
        """Check if army is clicked"""
        if not self.is_visible:
            return False
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx*dx + dy*dy <= (self.RADIUS * 2)**2

    def change_commander(self, commander):
        """Change commander"""
        old_commander = self.commander
        self.commander = commander
        print(f"✓ Commander changed: {old_commander} → {commander}")

    def change_assistant(self, assistant):
        """Change assistant"""
        old_assistant = self.assistant
        self.assistant = assistant
        print(f"✓ Assistant changed: {old_assistant} → {assistant}")

    def calc_speed(self):
        """Calculate current speed"""
        # Can be affected by various factors
        speed_modifier = 1.0

        # Morale effect
        if self.morale < 50:
            speed_modifier *= 0.8
        elif self.morale > 80:
            speed_modifier *= 1.2
        
        return self.BASE_SPEED * speed_modifier

    def add_unit(self, unit):
        """Add unit to army"""
        self.units.append(unit)
        print(f"✓ Unit added, total units: {len(self.units)}")

    def remove_unit(self, unit):
        """Remove unit from army"""
        if unit in self.units:
            self.units.remove(unit)
            print(f"✓ Unit removed, remaining units: {len(self.units)}")

    def modify_unit(self, unit, **data):
        """Modify unit attributes"""
        if unit in self.units:
            for key, value in data.items():
                setattr(unit, key, value)
            print(f"✓ Unit modified: {unit}")

    def get_units(self):
        """Get list of units"""
        return self.units.copy()
    
    def calculate_power(self):
        """Calculate total army power based on units and morale"""
        base_power = len(self.units) * 10
        morale_bonus = (self.morale / 100) * base_power * 0.5
        return int(base_power + morale_bonus)
    
    def __repr__(self):
        status = "in city" if self.city else "in field"
        return f"Army({self.commander}, Units: {len(self.units)}, {status})"