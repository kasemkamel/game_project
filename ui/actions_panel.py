# ui/actions_panel.py
import pygame
from systems.actions_system import ActionsSystem, ActionCategory


class ActionsPanel:
    """defines the actions panel UI component"""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.selected_entity = None
        self.actions_system = ActionsSystem()

        # colors
        self.bg_color = (30, 30, 40)
        self.border_color = (100, 100, 120)
        self.header_color = (50, 50, 70)
        self.action_color = (60, 60, 80)
        self.action_hover_color = (80, 80, 100)
        self.action_disabled_color = (40, 40, 50)
        self.text_color = (255, 255, 255)
        self.text_disabled_color = (120, 120, 120)

        # font settings
        self.title_font = pygame.font.Font(None, 28)
        self.action_font = pygame.font.Font(None, 24)
        self.desc_font = pygame.font.Font(None, 18)
        self.hotkey_font = pygame.font.Font(None, 20)

        # button settings
        self.action_height = 60
        self.action_spacing = 8
        self.padding = 12
        self.scroll_offset = 0
        self.max_visible_actions = (height - 80) // (
            self.action_height + self.action_spacing
        )

        # interaction state
        self.hovered_action = None
        self.categories_filter = None  # None = show all

        # category buttons
        self.category_buttons = {}
        self._setup_category_buttons()

    def _setup_category_buttons(self):
        """Set up category filter buttons"""
        button_width = 70
        button_height = 30
        spacing = 5
        start_x = self.rect.x + self.padding
        start_y = self.rect.y + 45

        categories = [
            (None, "all", "📋"),
            (ActionCategory.MOVEMENT, "Movement", "→"),
            (ActionCategory.MILITARY, "Military", "⚔️"),
            (ActionCategory.ESPIONAGE, "Espionage", "🕵️"),
            (ActionCategory.MANAGEMENT, "Management", "⚙️"),
            (ActionCategory.PRODUCTION, "Production", "🏗️"),
        ]

        for i, (category, name, icon) in enumerate(categories):
            x = start_x + (button_width + spacing) * i
            self.category_buttons[category] = {
                "rect": pygame.Rect(x, start_y, button_width, button_height),
                "name": name,
                "icon": icon,
            }

    def set_entity(self, entity):
        """Set the selected entity for the panel"""
        self.selected_entity = entity
        self.scroll_offset = 0
        self.categories_filter = None

    def get_visible_actions(self):
        """Get the visible actions based on the filter"""
        if not self.selected_entity:
            return []

        if self.categories_filter is None:
            return self.actions_system.get_actions(self.selected_entity)
        else:
            return self.actions_system.get_actions_by_category(
                self.selected_entity, self.categories_filter
            )

    def draw(self, screen):
        """ Draw the actions panel on the screen"""
        if not self.selected_entity:
            self._draw_empty_state(screen)
            return

        # Background of the panel
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        # Header of the panel
        self._draw_header(screen)

        # Category buttons
        self._draw_category_buttons(screen)

        # Actions list
        self._draw_actions(screen)

        # Scrollbar
        self._draw_scrollbar(screen)

    def _draw_empty_state(self, screen):
        """Draw the empty state when no entity is selected"""
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        text = self.title_font.render(
            "choose an entity to see its actions", True, self.text_disabled_color
        )
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def _draw_header(self, screen):
        """Draw the header of the panel"""
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 40)
        pygame.draw.rect(screen, self.header_color, header_rect)

        # Entity title
        entity_name = f"{self.selected_entity.__class__.__name__}"
        if hasattr(self.selected_entity, "name"):
            entity_name = f"{self.selected_entity.name}"

        title = self.title_font.render(entity_name, True, self.text_color)
        screen.blit(title, (self.rect.x + self.padding, self.rect.y + 8))

    def _draw_category_buttons(self, screen):
        """Draw category buttons"""
        for category, button_data in self.category_buttons.items():
            rect = button_data["rect"]
            is_active = self.categories_filter == category

            # Button color
            if is_active:
                color = self.action_hover_color
            else:
                color = self.action_color

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, self.border_color, rect, 1)

            # Button text
            icon_text = self.action_font.render(
                button_data["icon"], True, self.text_color
            )
            icon_rect = icon_text.get_rect(center=rect.center)
            screen.blit(icon_text, icon_rect)

    def _draw_actions(self, screen):
        """Draw the actions list"""
        actions = self.get_visible_actions()

        if not actions:
            no_actions_text = self.action_font.render(
                "No actions available", True, self.text_disabled_color
            )
            text_rect = no_actions_text.get_rect(
                center=(self.rect.centerx, self.rect.y + 150)
            )
            screen.blit(no_actions_text, text_rect)
            return

        # draw actions with clipping
        actions_start_y = self.rect.y + 85
        clip_rect = pygame.Rect(
            self.rect.x, actions_start_y, self.rect.width, self.rect.height - 85
        )
        screen.set_clip(clip_rect)

        y = actions_start_y - self.scroll_offset

        for i, action in enumerate(actions):
            action_rect = pygame.Rect(
                self.rect.x + self.padding,
                y,
                self.rect.width - 2 * self.padding - 20,  # Space for scrollbar
                self.action_height,
            )

            # Check visibility
            if (
                action_rect.bottom < actions_start_y
                or action_rect.top > self.rect.bottom
            ):
                y += self.action_height + self.action_spacing
                continue

            # Background color
            is_available = action.is_available(self.selected_entity)
            is_hovered = self.hovered_action == action

            if not is_available:
                bg_color = self.action_disabled_color
                text_color = self.text_disabled_color
            elif is_hovered:
                bg_color = self.action_hover_color
                text_color = self.text_color
            else:
                bg_color = self.action_color
                text_color = self.text_color

            pygame.draw.rect(screen, bg_color, action_rect, border_radius=4)
            pygame.draw.rect(screen, self.border_color, action_rect, 1, border_radius=4)

            # Icon
            if action.icon:
                icon_text = self.action_font.render(action.icon, True, text_color)
                screen.blit(icon_text, (action_rect.x + 8, action_rect.y + 8))

            # Action name
            name_text = self.action_font.render(action.name, True, text_color)
            screen.blit(name_text, (action_rect.x + 40, action_rect.y + 8))

            # Description
            desc_text = self.desc_font.render(action.description, True, text_color)
            screen.blit(desc_text, (action_rect.x + 40, action_rect.y + 32))

            # Hotkey
            if action.hotkey:
                hotkey_text = self.hotkey_font.render(
                    f"[{action.hotkey}]", True, text_color
                )
                hotkey_rect = hotkey_text.get_rect(
                    right=action_rect.right - 8, centery=action_rect.centery
                )
                screen.blit(hotkey_text, hotkey_rect)

            y += self.action_height + self.action_spacing

        screen.set_clip(None)

    def _draw_scrollbar(self, screen):
        """Draw the scrollbar"""
        actions = self.get_visible_actions()
        if len(actions) <= self.max_visible_actions:
            return

        scrollbar_width = 8
        scrollbar_x = self.rect.right - scrollbar_width - 4
        scrollbar_y = self.rect.y + 85
        scrollbar_height = self.rect.height - 85

        # Background of the scrollbar
        scrollbar_bg = pygame.Rect(
            scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height
        )
        pygame.draw.rect(
            screen, self.action_disabled_color, scrollbar_bg, border_radius=4
        )

        # Scrollbar handle
        total_content_height = len(actions) * (self.action_height + self.action_spacing)
        visible_ratio = scrollbar_height / total_content_height
        handle_height = max(30, scrollbar_height * visible_ratio)

        scroll_ratio = self.scroll_offset / (total_content_height - scrollbar_height)
        handle_y = scrollbar_y + scroll_ratio * (scrollbar_height - handle_height)

        handle_rect = pygame.Rect(scrollbar_x, handle_y, scrollbar_width, handle_height)
        pygame.draw.rect(screen, self.border_color, handle_rect, border_radius=4)

    def handle_event(self, event):
        """Handle events for the actions panel"""
        if not self.selected_entity:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check category buttons
                for category, button_data in self.category_buttons.items():
                    if button_data["rect"].collidepoint(event.pos):
                        self.categories_filter = category
                        self.scroll_offset = 0
                        return None

                # Check for clicks on actions
                if self.hovered_action:
                    return self.hovered_action

            elif event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 30)

            elif event.button == 5:  # Scroll down
                actions = self.get_visible_actions()
                max_scroll = max(
                    0,
                    len(actions) * (self.action_height + self.action_spacing)
                    - (self.rect.height - 85),
                )
                self.scroll_offset = min(max_scroll, self.scroll_offset + 30)

        elif event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)

        elif event.type == pygame.KEYDOWN:
            key_char = (
                event.unicode.upper()
                if event.unicode
                else pygame.key.name(event.key).upper()
            )
            actions = self.get_visible_actions()

            for action in actions:
                if action.hotkey and action.hotkey.upper() == key_char:
                    if action.is_available(self.selected_entity):
                        print(
                            f"✓ Keyboard shortcut [{action.hotkey}] triggered: {action.name}"
                        )
                        return action
                    else:
                        print(
                            f"⚠️ Action [{action.hotkey}] {action.name} is not available"
                        )
                        return None

        return None

    def _update_hover(self, mouse_pos):
        """Update the hovered action based on mouse position"""
        if not self.rect.collidepoint(mouse_pos):
            self.hovered_action = None
            return

        actions = self.get_visible_actions()
        actions_start_y = self.rect.y + 85
        y = actions_start_y - self.scroll_offset

        self.hovered_action = None

        for action in actions:
            action_rect = pygame.Rect(
                self.rect.x + self.padding,
                y,
                self.rect.width - 2 * self.padding - 20,
                self.action_height,
            )

            if action_rect.collidepoint(mouse_pos):
                self.hovered_action = action
                break

            y += self.action_height + self.action_spacing

