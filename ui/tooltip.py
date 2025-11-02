# ui/tooltip.py
import pygame

class Tooltip:
    def __init__(self):
        self.visible = False
        self.entity = None
        self.mouse_pos = (0, 0)
        
        # Style settings
        self.bg_color = (40, 40, 50, 200)  # Semi-transparent dark background
        self.border_color = (200, 200, 200)
        self.text_color = (255, 255, 255)
        self.padding = 10
        self.line_spacing = 5
        self.offset_x = 15
        self.offset_y = 15
        
        # Font
        try:
            self.font = pygame.font.Font(None, 24)
        except:
            self.font = pygame.font.SysFont('arial', 24)
    
    def update(self, entity, mouse_pos):
        """Update tooltip with entity information"""
        self.entity = entity
        self.mouse_pos = mouse_pos
        self.visible = entity is not None
    
    def hide(self):
        """Hide the tooltip"""
        self.visible = False
        self.entity = None
    
    def _get_entity_info(self, entity):
        """Extract displayable information from entity"""
        info_lines = []
        
        # Entity name/type
        if hasattr(entity, 'name'):
            info_lines.append(('Name', entity.name))
        else:
            info_lines.append(('Type', entity.__class__.__name__))
        
        # Owner information
        if hasattr(entity, 'owner'):
            owner_text = entity.owner if entity.owner else "Neutral"
            info_lines.append(('Owner', owner_text))
        
        # Army-specific info
        if hasattr(entity, 'destination'):
            status = "Moving" if entity.destination else "Idle"
            info_lines.append(('Status', status))
            if hasattr(entity, 'size'):
                info_lines.append(('Size', str(entity.size)))
        
        # Garrison info (for cities, castles, checkpoints)
        if hasattr(entity, 'garrison'):
            garrison_count = len(entity.garrison) if entity.garrison else 0
            info_lines.append(('Garrison', f"{garrison_count} armies"))
        
        # Position
        if hasattr(entity, 'x') and hasattr(entity, 'y'):
            info_lines.append(('Position', f"({int(entity.x)}, {int(entity.y)})"))
        
        return info_lines
    
    def render(self, screen):
        """Render the tooltip on screen"""
        if not self.visible or not self.entity:
            return
        
        # Get entity information
        info_lines = self._get_entity_info(self.entity)
        
        if not info_lines:
            return
        
        # Render text lines
        rendered_lines = []
        max_width = 0
        
        for label, value in info_lines:
            text_surface = self.font.render(f"{label}: {value}", True, self.text_color)
            rendered_lines.append(text_surface)
            max_width = max(max_width, text_surface.get_width())
        
        # Calculate tooltip dimensions
        total_height = sum(line.get_height() for line in rendered_lines)
        total_height += self.line_spacing * (len(rendered_lines) - 1)
        
        box_width = max_width + self.padding * 2
        box_height = total_height + self.padding * 2
        
        # Position tooltip near mouse, but keep it on screen
        tooltip_x = self.mouse_pos[0] + self.offset_x
        tooltip_y = self.mouse_pos[1] + self.offset_y
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Adjust if tooltip goes off-screen
        if tooltip_x + box_width > screen_width:
            tooltip_x = self.mouse_pos[0] - box_width - self.offset_x
        if tooltip_y + box_height > screen_height:
            tooltip_y = self.mouse_pos[1] - box_height - self.offset_y
        
        # Create semi-transparent surface
        tooltip_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        tooltip_surface.fill(self.bg_color)
        
        # Draw border
        pygame.draw.rect(tooltip_surface, self.border_color, 
                        (0, 0, box_width, box_height), 2)
        
        # Draw text lines
        current_y = self.padding
        for line in rendered_lines:
            tooltip_surface.blit(line, (self.padding, current_y))
            current_y += line.get_height() + self.line_spacing
        
        # Blit tooltip to screen
        screen.blit(tooltip_surface, (tooltip_x, tooltip_y))