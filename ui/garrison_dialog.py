# ui/garrison_dialog.py
import pygame


class GarrisonSelectionDialog:
    """Dialog to select which army to expel from a city garrison"""
    
    def __init__(self, city, screen_width, screen_height):
        self.city = city
        self.armies = list(city.garrison)  # Convert set to list
        self.selected_index = 0
        
        # Dialog dimensions
        self.width = 500
        self.height = min(500, 100 + len(self.armies) * 70)
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.border_color = (100, 100, 120)
        self.header_color = (50, 50, 70)
        self.item_color = (60, 60, 80)
        self.item_hover_color = (80, 80, 100)
        self.item_selected_color = (70, 100, 130)
        self.text_color = (255, 255, 255)
        self.text_secondary_color = (180, 180, 200)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.item_font = pygame.font.Font(None, 24)
        self.detail_font = pygame.font.Font(None, 20)
        self.instruction_font = pygame.font.Font(None, 18)
    
    def draw(self, screen):
        """Draw the selection dialog"""
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Main dialog background
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, self.border_color, self.rect, 3, border_radius=8)
        
        # Header
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 60)
        pygame.draw.rect(screen, self.header_color, header_rect, border_top_left_radius=8, border_top_right_radius=8)
        
        # Title
        title_text = f"garrison of {self.city.name}"
        title = self.title_font.render(title_text, True, self.text_color)
        title_rect = title.get_rect(centerx=self.rect.centerx, y=self.y + 18)
        screen.blit(title, title_rect)
        
        # Army list
        if len(self.armies) == 0:
            no_army_text = self.item_font.render("no armies in garrison", True, self.text_secondary_color)
            text_rect = no_army_text.get_rect(center=self.rect.center)
            screen.blit(no_army_text, text_rect)
            return
        
        y = self.y + 75
        for i, army in enumerate(self.armies):
            item_rect = pygame.Rect(self.x + 15, y, self.width - 30, 60)
            
            # Background color based on state
            if i == self.selected_index:
                color = self.item_selected_color
            else:
                color = self.item_color
            
            pygame.draw.rect(screen, color, item_rect, border_radius=5)
            pygame.draw.rect(screen, self.border_color, item_rect, 2, border_radius=5)
            
            # Army icon
            icon_text = self.item_font.render("⚔️", True, self.text_color)
            screen.blit(icon_text, (item_rect.x + 10, item_rect.y + 8))
            
            # Army name/commander
            army_name = army.name if hasattr(army, 'name') else f"جيش {i+1}"
            name_text = self.item_font.render(army_name, True, self.text_color)
            screen.blit(name_text, (item_rect.x + 45, item_rect.y + 8))
            
            # Army details (commander, units, power, etc.)
            details = []
            if hasattr(army, 'commander'):
                details.append(f"👤 {army.commander}")
            if hasattr(army, 'units'):
                details.append(f"⚔️ {len(army.units)} وحدة")
            if hasattr(army, 'calculate_power'):
                details.append(f"💪 {army.calculate_power()}")
            if hasattr(army, 'morale'):
                details.append(f"😊 {army.morale}%")
            
            details_str = " | ".join(details)
            details_text = self.detail_font.render(details_str, True, self.text_secondary_color)
            screen.blit(details_text, (item_rect.x + 45, item_rect.y + 33))
            
            y += 70
        
        # Instructions at bottom
        instructions_y = self.rect.bottom - 35
        
        # Background for instructions
        instr_bg = pygame.Rect(self.rect.x, instructions_y - 5, self.rect.width, 40)
        pygame.draw.rect(screen, self.header_color, instr_bg, border_bottom_left_radius=8, border_bottom_right_radius=8)

        instructions = "🖱️ Click to select | ⌨️ ↑↓ to navigate | ⏎ to confirm | ESC to cancel"
        inst_text = self.instruction_font.render(instructions, True, self.text_secondary_color)
        inst_rect = inst_text.get_rect(centerx=self.rect.centerx, centery=instructions_y + 15)
        screen.blit(inst_text, inst_rect)
    
    def handle_event(self, event):
        """
        Handle input events.
        Returns:
            - selected Army object if user selects one
            - "CANCEL" if user cancels
            - None if no action taken yet
        """
        if len(self.armies) == 0:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "CANCEL"
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "CANCEL"
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked on an army item
            y = self.y + 75
            for i, army in enumerate(self.armies):
                item_rect = pygame.Rect(self.x + 15, y, self.width - 30, 60)
                if item_rect.collidepoint(event.pos):
                    return army  # Return selected army
                y += 70
            
            # Check if clicked outside dialog to cancel
            if not self.rect.collidepoint(event.pos):
                return "CANCEL"
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover state
            y = self.y + 75
            old_index = self.selected_index
            
            for i, army in enumerate(self.armies):
                item_rect = pygame.Rect(self.x + 15, y, self.width - 30, 60)
                if item_rect.collidepoint(event.pos):
                    self.selected_index = i
                    break
                y += 70
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "CANCEL"
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if 0 <= self.selected_index < len(self.armies):
                    return self.armies[self.selected_index]
            
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.armies) - 1, self.selected_index + 1)
            
            elif event.key == pygame.K_HOME:
                self.selected_index = 0
            
            elif event.key == pygame.K_END:
                self.selected_index = len(self.armies) - 1
        
        return None