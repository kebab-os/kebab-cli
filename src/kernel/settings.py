"""Settings panel UI management"""

import pygame
from .config import TERM_CONFIG


class SettingsPanel:
    """Manages the settings UI panel on the right side"""
    
    def __init__(self, width=300):
        self.width = width
        self.visible = False
        self.padding = 15
        self.slider_height = 20
        self.label_height = 20
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Load settings button icon
        try:
            self.settings_icon = pygame.image.load('static/system/settings.png')
            self.settings_icon = pygame.transform.scale(self.settings_icon, (16, 16))
        except:
            self.settings_icon = None
        
        # Settings with sliders (name, min, max, current, config_key)
        self.sliders = [
            ('Font Size', 8, 24, TERM_CONFIG['font_size'], 'font_size'),
            ('Line Height', 12, 40, TERM_CONFIG['line_height'], 'line_height'),
        ]
        
        # Color settings (name, current_color_key)
        self.colors = [
            ('Foreground', 'fg_color'),
            ('Background', 'bg_color'),
            ('Cursor', 'cursor_color'),
            ('Prompt', 'prompt_color'),
        ]
        
        self.hovered_slider = None
        self.dragging_slider = None
        
    def get_rect(self, screen_width, screen_height):
        """Get the panel rectangle"""
        return pygame.Rect(screen_width - self.width, 0, self.width, screen_height)
    
    def get_button_rect(self, screen_width, menu_bar_height):
        """Get the settings button rectangle (within the menu bar on the top-right)"""
        button_size = 24
        x = screen_width - button_size - 12
        y = (menu_bar_height - button_size) // 2
        return pygame.Rect(x, y, button_size, button_size)
    
    def get_close_button_rect(self, screen_width):
        """Get the close button rectangle (top-right of settings panel)"""
        button_size = 28
        # Position on the right side of the settings panel, well within it
        return pygame.Rect(screen_width - button_size - self.padding - 2, self.padding + 8, button_size, button_size)
    
    def toggle(self):
        """Toggle settings panel visibility"""
        self.visible = not self.visible
        self.dragging_slider = None
    
    def scroll(self, direction):
        """Scroll the settings panel (direction: 1 for up, -1 for down)"""
        if not self.visible:
            return
        # Scroll step
        step = 30
        self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - direction * step))
    
    def handle_mouse_motion(self, pos, screen_width, screen_height):
        """Handle mouse motion for slider hovering"""
        if not self.visible:
            return None
        
        panel_rect = self.get_rect(screen_width, screen_height)
        if not panel_rect.collidepoint(pos):
            self.hovered_slider = None
            return None
        
        # Check which slider is being hovered
        y_offset = self.padding + 40 - self.scroll_offset
        for i, (name, min_val, max_val, current, key) in enumerate(self.sliders):
            # Slider rect matches render position (with label offset)
            slider_rect = pygame.Rect(
                screen_width - self.width + self.padding,
                y_offset + self.label_height + 5,
                self.width - 2 * self.padding,
                self.slider_height
            )
            if slider_rect.collidepoint(pos):
                self.hovered_slider = i
                return i
            y_offset += self.label_height + self.slider_height + 15
        
        # Check color sliders
        color_y = y_offset + 25
        color_idx = 0
        for name, color_key in self.colors:
            color_y += 25
            for j, channel in enumerate(['R', 'G', 'B']):
                # Color slider rect matches render position
                channel_slider_rect = pygame.Rect(
                    screen_width - self.width + self.padding,
                    color_y + self.label_height + 2,
                    self.width - 2 * self.padding,
                    self.slider_height
                )
                if channel_slider_rect.collidepoint(pos):
                    self.hovered_slider = (color_idx, j)
                    return (color_idx, j)
                color_y += self.label_height + self.slider_height + 5
            color_idx += 1
        
        self.hovered_slider = None
        return None
    
    def handle_mouse_down(self, pos, screen_width, screen_height):
        """Handle mouse down on slider"""
        if not self.visible:
            return
        
        idx = self.handle_mouse_motion(pos, screen_width, screen_height)
        if idx is not None:
            self.dragging_slider = idx
    
    def handle_mouse_up(self):
        """Handle mouse up"""
        self.dragging_slider = None
    
    def update_slider_from_mouse(self, mouse_x, screen_width):
        """Update slider value from mouse position"""
        if self.dragging_slider is None:
            return
        
        # Calculate slider position
        slider_x = screen_width - self.width + self.padding
        slider_width = self.width - 2 * self.padding
        
        # Clamp mouse to slider bounds
        rel_x = max(0, min(slider_width, mouse_x - slider_x))
        
        # Handle regular sliders
        if isinstance(self.dragging_slider, int):
            idx = self.dragging_slider
            name, min_val, max_val, current, key = self.sliders[idx]
            ratio = rel_x / slider_width if slider_width > 0 else 0
            new_value = int(min_val + (max_val - min_val) * ratio)
            self.sliders[idx] = (name, min_val, max_val, new_value, key)
            return new_value, key
        
        # Handle color sliders
        if isinstance(self.dragging_slider, tuple):
            color_idx, channel_idx = self.dragging_slider
            ratio = rel_x / slider_width if slider_width > 0 else 0
            new_value = int(ratio * 255)
            
            color_key = self.colors[color_idx][1]
            color_value = list(TERM_CONFIG.get(color_key, (255, 255, 255)))
            color_value[channel_idx] = new_value
            TERM_CONFIG[color_key] = tuple(color_value)
            return new_value, color_key
        
        return None
    
    def get_slider_value(self, key):
        """Get current slider value by config key"""
        for name, min_val, max_val, current, slider_key in self.sliders:
            if slider_key == key:
                return current
        return None
    
    def render(self, screen, screen_width, screen_height, font):
        """Render settings panel"""
        if not self.visible:
            return
        
        panel_rect = self.get_rect(screen_width, screen_height)
        
        # Draw panel background
        pygame.draw.rect(screen, (20, 20, 20), panel_rect)
        pygame.draw.line(screen, (60, 60, 60), (panel_rect.left, 0), (panel_rect.left, screen_height), 2)
        
        # Create a clip rect for scrollable content
        content_rect = pygame.Rect(panel_rect.left, self.padding + 35, self.width, screen_height - self.padding - 35)
        screen.set_clip(content_rect)
        
        # Draw title (outside scroll area)
        screen.set_clip(None)
        title_font = pygame.font.SysFont('consolas', 16, bold=True)
        title_surf = title_font.render('Settings', True, (200, 200, 200))
        screen.blit(title_surf, (panel_rect.left + self.padding, self.padding))
        screen.set_clip(content_rect)
        
        # Draw sliders
        y_offset = self.padding + 40 - self.scroll_offset
        for i, (name, min_val, max_val, current, key) in enumerate(self.sliders):
            # Label
            label_surf = font.render(f'{name}: {current}', True, (180, 180, 180))
            screen.blit(label_surf, (panel_rect.left + self.padding, y_offset))
            
            # Slider background
            slider_rect = pygame.Rect(
                panel_rect.left + self.padding,
                y_offset + self.label_height + 5,
                self.width - 2 * self.padding,
                self.slider_height
            )
            pygame.draw.rect(screen, (40, 40, 40), slider_rect)
            pygame.draw.rect(screen, (80, 80, 80), slider_rect, 1)
            
            # Slider fill
            ratio = (current - min_val) / (max_val - min_val) if (max_val - min_val) > 0 else 0
            fill_width = int((self.width - 2 * self.padding) * ratio)
            fill_rect = pygame.Rect(slider_rect.left, slider_rect.top, fill_width, self.slider_height)
            color = (0, 150, 255) if i == self.hovered_slider else (0, 120, 200)
            pygame.draw.rect(screen, color, fill_rect)
            
            y_offset += self.label_height + self.slider_height + 15
        
        # Draw colors
        color_y = y_offset
        color_label_font = pygame.font.SysFont('consolas', 12)
        color_label_surf = color_label_font.render('Colors:', True, (200, 200, 200))
        screen.blit(color_label_surf, (panel_rect.left + self.padding, color_y))
        
        color_y += 25
        for color_idx, (name, color_key) in enumerate(self.colors):
            color_value = TERM_CONFIG.get(color_key, (255, 255, 255))
            
            # Color name
            color_name_surf = font.render(name, True, (180, 180, 180))
            screen.blit(color_name_surf, (panel_rect.left + self.padding, color_y))
            
            # Color swatch
            swatch_size = 20
            swatch_rect = pygame.Rect(
                panel_rect.left + self.width - self.padding - swatch_size,
                color_y,
                swatch_size,
                swatch_size
            )
            pygame.draw.rect(screen, color_value, swatch_rect)
            pygame.draw.rect(screen, (100, 100, 100), swatch_rect, 1)
            
            color_y += 30
            
            # RGB sliders
            channels = ['R', 'G', 'B']
            for j, channel in enumerate(channels):
                r, g, b = color_value
                channel_values = [r, g, b]
                current_val = channel_values[j]
                
                # Label
                channel_label = f'{channel}: {current_val}'
                channel_surf = font.render(channel_label, True, (150, 150, 150))
                screen.blit(channel_surf, (panel_rect.left + self.padding, color_y))
                
                # Slider background
                slider_rect = pygame.Rect(
                    panel_rect.left + self.padding,
                    color_y + self.label_height + 2,
                    self.width - 2 * self.padding,
                    self.slider_height
                )
                pygame.draw.rect(screen, (40, 40, 40), slider_rect)
                pygame.draw.rect(screen, (80, 80, 80), slider_rect, 1)
                
                # Slider fill
                ratio = current_val / 255.0
                fill_width = int((self.width - 2 * self.padding) * ratio)
                fill_rect = pygame.Rect(slider_rect.left, slider_rect.top, fill_width, self.slider_height)
                
                # Color the slider based on channel
                channel_colors = [(200, 100, 100), (100, 200, 100), (100, 100, 200)]
                is_hovered = self.hovered_slider == (color_idx, j)
                color = (255, 150, 150) if (is_hovered and j == 0) else \
                        (150, 255, 150) if (is_hovered and j == 1) else \
                        (150, 150, 255) if (is_hovered and j == 2) else \
                        channel_colors[j]
                pygame.draw.rect(screen, color, fill_rect)
                
                color_y += self.label_height + self.slider_height + 5
            
            color_y += 10
        
        # Update max scroll based on content height
        self.max_scroll = max(0, color_y - (screen_height - self.padding - 35))
        
        # Reset clip
        screen.set_clip(None)
    
    def render_button(self, screen, screen_width, font, menu_bar_height):
        """Render the settings button inside the menu bar (rounded)"""
        button_rect = self.get_button_rect(screen_width, menu_bar_height)

        # Draw rounded button background
        button_color = (0, 100, 150) if self.visible else (0, 80, 120)
        pygame.draw.rect(screen, button_color, button_rect, border_radius=6)
        pygame.draw.rect(screen, (100, 150, 200), button_rect, 2, border_radius=6)

        # Draw icon (image or fallback gear character)
        center_x = button_rect.centerx
        center_y = button_rect.centery

        if self.settings_icon:
            icon = pygame.transform.scale(self.settings_icon, (20, 20))
            icon_rect = icon.get_rect(center=(center_x, center_y))
            screen.blit(icon, icon_rect)
        else:
            # Fallback to gear character if image fails to load
            icon_font = pygame.font.SysFont('consolas', 18, bold=True)
            icon_surf = icon_font.render('⚙', True, (200, 200, 200))
            icon_rect = icon_surf.get_rect(center=(center_x, center_y))
            screen.blit(icon_surf, icon_rect)

        return button_rect
    
    def render_close_button(self, screen, screen_width):
        """Render close button on the settings panel"""
        if not self.visible:
            return None
        
        close_rect = self.get_close_button_rect(screen_width)
        
        # Draw button background - more visible red
        pygame.draw.rect(screen, (80, 30, 30), close_rect)
        pygame.draw.rect(screen, (200, 80, 80), close_rect, 2)
        
        # Draw X icon
        center_x = close_rect.centerx
        center_y = close_rect.centery
        icon_font = pygame.font.SysFont('consolas', 20, bold=True)
        icon_surf = icon_font.render('X', True, (255, 100, 100))
        icon_rect = icon_surf.get_rect(center=(center_x, center_y))
        screen.blit(icon_surf, icon_rect)
        
        return close_rect
