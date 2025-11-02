# ui/loading_screen.py
import pygame

class LoadingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.progress = 0.0
        self.status_text = "Initializing..."
        
        # Colors
        self.bg_color = (20, 20, 30) 
        self.bar_bg_color = (50, 50, 60)
        self.bar_fill_color = (100, 150, 255)
        self.text_color = (0, 0, 0)
        
        # Font
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 32)
        except:
            self.font_large = pygame.font.SysFont('arial', 48)
            self.font_small = pygame.font.SysFont('arial', 32)
        
        # Background image (optional - will use solid color if not found)
        self.background_image = None
        try:
            self.background_image = pygame.image.load("assets/images/loading_background.jpg")
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
        except:
            print("Loading background image not found, using solid color")
        
        # Loading bar dimensions
        self.bar_width = 600
        self.bar_height = 40
        self.bar_x = (self.width - self.bar_width) // 2
        self.bar_y = (self.height - self.bar_height) // 2 + 200
    
    def update(self, progress, status_text="Loading..."):
        """Update progress (0.0 to 1.0) and status text"""
        self.progress = min(1.0, max(0.0, progress))
        self.status_text = status_text

    def get_progress(self):
        """Get current progress (0.0 to 1.0)"""
        return self.progress

    def render(self):
        """Render the loading screen"""
        # Draw background
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(self.bg_color)
        
        # Draw title
        title_text = self.font_large.render("Strategic Province Engine", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw loading bar background
        pygame.draw.rect(self.screen, self.bar_bg_color, 
                        (self.bar_x, self.bar_y, self.bar_width, self.bar_height))
        
        # Draw loading bar fill
        fill_width = int(self.bar_width * self.progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.bar_fill_color,
                           (self.bar_x, self.bar_y, fill_width, self.bar_height))
        
        # Draw loading bar border
        pygame.draw.rect(self.screen, self.text_color,
                        (self.bar_x, self.bar_y, self.bar_width, self.bar_height), 2)
        
        # Draw percentage
        percent_text = self.font_small.render(f"{int(self.progress * 100)}%", True, self.text_color)
        percent_rect = percent_text.get_rect(center=(self.width // 2, self.bar_y + self.bar_height // 2))
        self.screen.blit(percent_text, percent_rect)
        
        # Draw status text
        status = self.font_small.render(self.status_text, True, self.text_color)
        status_rect = status.get_rect(center=(self.width // 2, self.bar_y + self.bar_height + 50))
        self.screen.blit(status, status_rect)
        
        pygame.display.flip()