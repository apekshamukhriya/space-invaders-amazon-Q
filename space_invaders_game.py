import pygame
import sys
import json
import time
import math
import random
from datetime import datetime
from enum import Enum

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1000, 700
FPS = 60

# Color Themes
class Theme(Enum):
    CLASSIC = 0
    NEON = 1
    SUNSET = 2
    OCEAN = 3
    FOREST = 4

# Difficulty Levels
class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2

# Theme Colors
THEME_COLORS = {
    Theme.CLASSIC: {
        'bg': (0, 0, 0),
        'player': (0, 255, 0),
        'enemy': (255, 0, 0),
        'bullet': (255, 255, 0),
        'text': (255, 255, 255),
        'accent': (0, 255, 255)
    },
    Theme.NEON: {
        'bg': (10, 10, 40),
        'player': (0, 255, 255),
        'enemy': (255, 0, 255),
        'bullet': (255, 255, 0),
        'text': (0, 255, 255),
        'accent': (255, 0, 128)
    },
    Theme.SUNSET: {
        'bg': (50, 0, 50),
        'player': (255, 165, 0),
        'enemy': (255, 69, 0),
        'bullet': (255, 215, 0),
        'text': (255, 255, 255),
        'accent': (255, 105, 180)
    },
    Theme.OCEAN: {
        'bg': (0, 50, 100),
        'player': (0, 191, 255),
        'enemy': (70, 130, 180),
        'bullet': (240, 248, 255),
        'text': (240, 248, 255),
        'accent': (127, 255, 212)
    },
    Theme.FOREST: {
        'bg': (0, 50, 0),
        'player': (50, 205, 50),
        'enemy': (139, 69, 19),
        'bullet': (255, 255, 0),
        'text': (152, 251, 152),
        'accent': (255, 215, 0)
    }
}

# Difficulty Settings
DIFFICULTY_SETTINGS = {
    Difficulty.EASY: {
        'alien_rows': 3,
        'alien_cols': 6,
        'alien_speed_mult': 0.8,
        'obstacle_rate': 180,
        'points_mult': 1
    },
    Difficulty.MEDIUM: {
        'alien_rows': 5,
        'alien_cols': 8,
        'alien_speed_mult': 1.0,
        'obstacle_rate': 120,
        'points_mult': 1.5
    },
    Difficulty.HARD: {
        'alien_rows': 7,
        'alien_cols': 10,
        'alien_speed_mult': 1.5,
        'obstacle_rate': 60,
        'points_mult': 2.0
    }
}

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders Deluxe")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 64)
        
        # Game state
        self.state = "MENU"  # MENU, PLAYING, GAME_OVER, PAUSED, SETTINGS, LEADERBOARD
        self.score = 0
        self.high_score = self.load_high_score()
        self.start_time = 0
        self.bullets_fired = 0
        self.hits = 0
        self.level = 1
        self.paused = False
        
        # Settings
        self.theme = Theme.CLASSIC
        self.difficulty = Difficulty.MEDIUM
        
        # Player
        self.player_x = WIDTH // 2 - 25
        self.player_y = HEIGHT - 80
        self.player_speed = 6
        self.bullets = []
        
        # Aliens
        self.aliens = []
        self.alien_speed = 1
        self.alien_direction = 1
        
        # Obstacles
        self.obstacles = []
        self.obstacle_timer = 0
        
        # Menu
        self.menu_selection = 0
        self.menu_options = ["Start Game", "Settings", "Leaderboard", "Quit"]
        self.settings_selection = 0
        self.settings_options = ["Theme", "Difficulty", "Back"]
        
        # Graffiti elements
        self.graffiti = self.generate_graffiti()
        
        # Leaderboard
        self.leaderboard = self.load_leaderboard()
        
        # Initialize game
        self.create_aliens()
    
    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as f:
                return json.load(f).get('high_score', 0)
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def load_leaderboard(self):
        try:
            with open('leaderboard.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_leaderboard(self):
        try:
            with open('leaderboard.json', 'w') as f:
                json.dump(self.leaderboard, f)
        except:
            pass
    
    def generate_graffiti(self):
        elements = []
        colors = list(THEME_COLORS[self.theme].values())
        
        for _ in range(20):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(10, 30)
            color = random.choice(colors)
            shape = random.choice(['circle', 'star', 'triangle', 'rect'])
            elements.append({'x': x, 'y': y, 'size': size, 'color': color, 'shape': shape})
        
        return elements
    
    def create_aliens(self):
        self.aliens = []
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        
        for row in range(settings['alien_rows']):
            for col in range(settings['alien_cols']):
                x = 100 + col * 80
                y = 50 + row * 60
                alien_type = random.choice(['ufo', 'ship', 'fighter'])
                self.aliens.append({'x': x, 'y': y, 'type': alien_type})
    
    def draw_player(self):
        colors = THEME_COLORS[self.theme]
        
        # Draw spaceship
        points = [
            (self.player_x + 25, self.player_y),
            (self.player_x + 10, self.player_y + 30),
            (self.player_x + 40, self.player_y + 30)
        ]
        pygame.draw.polygon(self.screen, colors['player'], points)
        
        # Cockpit
        pygame.draw.circle(self.screen, colors['accent'], (self.player_x + 25, self.player_y + 15), 8)
        
        # Engine glow
        glow_size = 3 + int(2 * math.sin(time.time() * 10))
        pygame.draw.circle(self.screen, colors['bullet'], (self.player_x + 25, self.player_y + 25), glow_size)
    
    def draw_aliens(self):
        colors = THEME_COLORS[self.theme]
        
        for alien in self.aliens:
            if alien['type'] == 'ufo':
                # UFO shape
                pygame.draw.ellipse(self.screen, colors['enemy'], (alien['x'], alien['y'] + 5, 40, 15))
                pygame.draw.ellipse(self.screen, colors['accent'], (alien['x'] + 5, alien['y'], 30, 10))
                
                # Lights (animated)
                for i in range(3):
                    light_on = (int(time.time() * 5) + i) % 3 == 0
                    light_color = colors['bullet'] if light_on else colors['accent']
                    pygame.draw.circle(self.screen, light_color, (alien['x'] + 10 + i * 10, alien['y'] + 10), 2)
            
            elif alien['type'] == 'ship':
                # Ship shape
                pygame.draw.rect(self.screen, colors['enemy'], (alien['x'], alien['y'], 40, 20))
                pygame.draw.polygon(self.screen, colors['enemy'], [
                    (alien['x'] + 20, alien['y'] - 10),
                    (alien['x'], alien['y']),
                    (alien['x'] + 40, alien['y'])
                ])
            
            else:  # fighter
                # Fighter shape
                pygame.draw.polygon(self.screen, colors['enemy'], [
                    (alien['x'] + 20, alien['y']),
                    (alien['x'], alien['y'] + 20),
                    (alien['x'] + 40, alien['y'] + 20)
                ])
                pygame.draw.rect(self.screen, colors['accent'], (alien['x'] + 15, alien['y'] + 5, 10, 10))
    
    def draw_obstacles(self):
        colors = THEME_COLORS[self.theme]
        
        for obstacle in self.obstacles:
            if obstacle['type'] == 'asteroid':
                # Asteroid with crater
                pygame.draw.circle(self.screen, obstacle['color'], (int(obstacle['x']), int(obstacle['y'])), obstacle['size'])
                pygame.draw.circle(self.screen, colors['bg'], (int(obstacle['x'] - obstacle['size']/3), 
                                                            int(obstacle['y'] - obstacle['size']/3)), obstacle['size']//3)
            else:  # enemy ship
                # Small enemy ship
                pygame.draw.rect(self.screen, obstacle['color'], (obstacle['x'] - 15, obstacle['y'] - 10, 30, 20))
                pygame.draw.circle(self.screen, colors['bullet'], (int(obstacle['x']), int(obstacle['y'])), 5)
    
    def draw_bullets(self):
        colors = THEME_COLORS[self.theme]
        
        for bullet in self.bullets:
            # Bullet with trail
            pygame.draw.rect(self.screen, colors['bullet'], (bullet[0], bullet[1], 4, 10))
            
            # Animated trail
            trail_length = random.randint(5, 15)
            pygame.draw.rect(self.screen, colors['accent'], (bullet[0], bullet[1] + 10, 4, trail_length))
    
    def draw_graffiti(self):
        for element in self.graffiti:
            alpha = 30 + int(20 * math.sin(time.time() + element['x'] * 0.01))
            
            if element['shape'] == 'circle':
                s = pygame.Surface((element['size']*2, element['size']*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*element['color'], alpha), (element['size'], element['size']), element['size'])
                self.screen.blit(s, (element['x']-element['size'], element['y']-element['size']))
            
            elif element['shape'] == 'star':
                points = []
                for i in range(5):
                    angle = i * 2 * math.pi / 5 - math.pi/2
                    x = element['size'] + element['size'] * math.cos(angle)
                    y = element['size'] + element['size'] * math.sin(angle)
                    points.append((x, y))
                
                s = pygame.Surface((element['size']*2, element['size']*2), pygame.SRCALPHA)
                if len(points) >= 3:
                    pygame.draw.polygon(s, (*element['color'], alpha), points)
                self.screen.blit(s, (element['x']-element['size'], element['y']-element['size']))
            
            elif element['shape'] == 'triangle':
                s = pygame.Surface((element['size']*2, element['size']*2), pygame.SRCALPHA)
                points = [
                    (element['size'], 0),
                    (0, element['size']*2),
                    (element['size']*2, element['size']*2)
                ]
                pygame.draw.polygon(s, (*element['color'], alpha), points)
                self.screen.blit(s, (element['x']-element['size'], element['y']-element['size']))
            
            elif element['shape'] == 'rect':
                s = pygame.Surface((element['size']*2, element['size']), pygame.SRCALPHA)
                pygame.draw.rect(s, (*element['color'], alpha), (0, 0, element['size']*2, element['size']))
                self.screen.blit(s, (element['x']-element['size'], element['y']-element['size']//2))
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[1] -= 8
            if bullet[1] < 0:
                self.bullets.remove(bullet)
    
    def update_aliens(self):
        if not self.aliens:
            return
        
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        current_speed = self.alien_speed * settings['alien_speed_mult']
        move_down = False
        
        for alien in self.aliens:
            alien['x'] += current_speed * self.alien_direction
            if alien['x'] <= 0 or alien['x'] >= WIDTH - 40:
                move_down = True
            
            # Game over if aliens reach bottom
            if alien['y'] >= HEIGHT - 120:
                self.state = "GAME_OVER"
        
        if move_down:
            self.alien_direction *= -1
            for alien in self.aliens:
                alien['y'] += 25
    
    def update_obstacles(self):
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        self.obstacle_timer += 1
        
        # Spawn new obstacles
        if self.obstacle_timer >= settings['obstacle_rate']:
            self.obstacle_timer = 0
            
            # Create random obstacle
            obstacle_type = random.choice(['asteroid', 'enemy'])
            obstacle_color = THEME_COLORS[self.theme]['enemy']
            
            self.obstacles.append({
                'x': random.randint(50, WIDTH-50),
                'y': -30,
                'speed': random.randint(2, 5) * settings['alien_speed_mult'],
                'type': obstacle_type,
                'color': obstacle_color,
                'size': random.randint(15, 25)
            })
        
        # Move obstacles
        for obstacle in self.obstacles[:]:
            obstacle['y'] += obstacle['speed']
            if obstacle['y'] > HEIGHT:
                self.obstacles.remove(obstacle)
    
    def check_collisions(self):
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        
        # Bullet-alien collisions
        for bullet in self.bullets[:]:
            for alien in self.aliens[:]:
                if (bullet[0] < alien['x'] + 40 and bullet[0] + 4 > alien['x'] and
                    bullet[1] < alien['y'] + 20 and bullet[1] + 10 > alien['y']):
                    self.bullets.remove(bullet)
                    self.aliens.remove(alien)
                    self.score += int(10 * settings['points_mult'])
                    self.hits += 1
                    break
        
        # Bullet-obstacle collisions
        for bullet in self.bullets[:]:
            for obstacle in self.obstacles[:]:
                if (bullet[0] < obstacle['x'] + obstacle['size'] and bullet[0] + 4 > obstacle['x'] - obstacle['size'] and
                    bullet[1] < obstacle['y'] + obstacle['size'] and bullet[1] + 10 > obstacle['y'] - obstacle['size']):
                    self.bullets.remove(bullet)
                    self.obstacles.remove(obstacle)
                    self.score += int(5 * settings['points_mult'])
                    self.hits += 1
                    break
        
        # Player-obstacle collisions
        for obstacle in self.obstacles[:]:
            if (self.player_x < obstacle['x'] + obstacle['size'] and self.player_x + 50 > obstacle['x'] - obstacle['size'] and
                self.player_y < obstacle['y'] + obstacle['size'] and self.player_y + 30 > obstacle['y'] - obstacle['size']):
                self.state = "GAME_OVER"
    
    def draw_hud(self):
        colors = THEME_COLORS[self.theme]
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, colors['text'])
        self.screen.blit(score_text, (10, 10))
        
        # High score
        high_score_text = self.font.render(f"High: {self.high_score}", True, colors['accent'])
        self.screen.blit(high_score_text, (10, 40))
        
        # Level and time
        time_played = time.time() - self.start_time if self.start_time > 0 else 0
        level_text = self.font.render(f"Level: {self.level}", True, colors['text'])
        time_text = self.font.render(f"Time: {int(time_played)}s", True, colors['text'])
        self.screen.blit(level_text, (10, 70))
        self.screen.blit(time_text, (10, 100))
        
        # Difficulty and theme
        diff_text = self.font.render(f"Difficulty: {self.difficulty.name}", True, colors['accent'])
        theme_text = self.font.render(f"Theme: {self.theme.name}", True, colors['accent'])
        self.screen.blit(diff_text, (WIDTH - 200, 10))
        self.screen.blit(theme_text, (WIDTH - 200, 40))
        
        # Accuracy
        if self.bullets_fired > 0:
            accuracy = (self.hits / self.bullets_fired) * 100
            acc_text = self.font.render(f"Accuracy: {accuracy:.1f}%", True, colors['text'])
            self.screen.blit(acc_text, (WIDTH - 200, 70))
        
        # Controls
        controls = ["P-Pause", "R-Restart", "ESC-Menu"]
        for i, control in enumerate(controls):
            control_text = self.font.render(control, True, colors['text'])
            self.screen.blit(control_text, (WIDTH - 120, HEIGHT - 80 + i * 25))
    
    def draw_menu(self):
        colors = THEME_COLORS[self.theme]
        self.screen.fill(colors['bg'])
        
        # Draw graffiti background
        self.draw_graffiti()
        
        # Title with animation
        title_offset = int(5 * math.sin(time.time() * 2))
        title = self.big_font.render("SPACE INVADERS", True, colors['accent'])
        title_rect = title.get_rect(center=(WIDTH//2, 120 + title_offset))
        self.screen.blit(title, title_rect)
        
        # Menu options
        for i, option in enumerate(self.menu_options):
            color = colors['accent'] if i == self.menu_selection else colors['text']
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(WIDTH//2, 250 + i * 50))
            
            # Highlight selected option
            if i == self.menu_selection:
                highlight_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 5, text_rect.width + 40, text_rect.height + 10)
                pygame.draw.rect(self.screen, color + (50,), highlight_rect, 2)
            
            self.screen.blit(text, text_rect)
        
        # Instructions
        inst_text = self.font.render("Arrow Keys + Enter to navigate", True, colors['text'])
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGHT - 80))
        self.screen.blit(inst_text, inst_rect)
        
        # High score
        hs_text = self.font.render(f"High Score: {self.high_score}", True, colors['accent'])
        hs_rect = hs_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
        self.screen.blit(hs_text, hs_rect)
    
    def draw_settings(self):
        colors = THEME_COLORS[self.theme]
        self.screen.fill(colors['bg'])
        
        # Draw graffiti background
        self.draw_graffiti()
        
        # Title
        title = self.big_font.render("SETTINGS", True, colors['accent'])
        title_rect = title.get_rect(center=(WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Settings options
        settings_info = [
            f"Theme: {self.theme.name}",
            f"Difficulty: {self.difficulty.name}",
            "Back to Menu"
        ]
        
        for i, info in enumerate(settings_info):
            color = colors['accent'] if i == self.settings_selection else colors['text']
            text = self.font.render(info, True, color)
            text_rect = text.get_rect(center=(WIDTH//2, 200 + i * 60))
            
            # Highlight selected option
            if i == self.settings_selection:
                highlight_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 5, text_rect.width + 40, text_rect.height + 10)
                pygame.draw.rect(self.screen, color + (50,), highlight_rect, 2)
            
            self.screen.blit(text, text_rect)
        
        # Theme preview
        if self.settings_selection == 0:
            # Show theme preview boxes
            preview_y = 350
            box_size = 40
            gap = 10
            total_width = (box_size + gap) * len(Theme)
            start_x = WIDTH//2 - total_width//2
            
            for i, theme in enumerate(Theme):
                theme_colors = THEME_COLORS[theme]
                box_x = start_x + i * (box_size + gap)
                
                # Draw theme box
                pygame.draw.rect(self.screen, theme_colors['bg'], (box_x, preview_y, box_size, box_size))
                pygame.draw.rect(self.screen, theme_colors['player'], (box_x + 5, preview_y + 5, 10, 10))
                pygame.draw.rect(self.screen, theme_colors['enemy'], (box_x + 25, preview_y + 5, 10, 10))
                pygame.draw.rect(self.screen, theme_colors['bullet'], (box_x + 15, preview_y + 20, 10, 10))
                
                # Highlight current theme
                if theme == self.theme:
                    pygame.draw.rect(self.screen, theme_colors['accent'], (box_x - 2, preview_y - 2, box_size + 4, box_size + 4), 2)
            
            # Theme names
            theme_names = [t.name for t in Theme]
            names_text = self.font.render(" | ".join(theme_names), True, colors['text'])
            names_rect = names_text.get_rect(center=(WIDTH//2, preview_y + box_size + 20))
            self.screen.blit(names_text, names_rect)
        
        # Difficulty info
        elif self.settings_selection == 1:
            diff_info = [
                f"EASY: Fewer aliens, slower speed",
                f"MEDIUM: Balanced gameplay",
                f"HARD: More aliens, faster speed, higher score"
            ]
            
            for i, info in enumerate(diff_info):
                text_color = colors['accent'] if i == self.difficulty.value else colors['text']
                diff_text = self.font.render(info, True, text_color)
                diff_rect = diff_text.get_rect(center=(WIDTH//2, 350 + i * 30))
                self.screen.blit(diff_text, diff_rect)
        
        # Instructions
        inst_text = self.font.render("Enter to change | ESC to go back", True, colors['text'])
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
        self.screen.blit(inst_text, inst_rect)
    
    def draw_leaderboard(self):
        colors = THEME_COLORS[self.theme]
        self.screen.fill(colors['bg'])
        
        # Draw graffiti background
        self.draw_graffiti()
        
        # Title
        title = self.big_font.render("LEADERBOARD", True, colors['accent'])
        title_rect = title.get_rect(center=(WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        if not self.leaderboard:
            no_scores = self.font.render("No scores yet! Play to set records!", True, colors['text'])
            no_rect = no_scores.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(no_scores, no_rect)
        else:
            # Headers
            headers = ["Rank", "Score", "Time", "Level", "Difficulty"]
            header_text = " | ".join(headers)
            header_surface = self.font.render(header_text, True, colors['accent'])
            header_rect = header_surface.get_rect(center=(WIDTH//2, 140))
            self.screen.blit(header_surface, header_rect)
            
            # Draw leaderboard entries
            for i, entry in enumerate(self.leaderboard[:8]):
                rank = f"{i+1}."
                score = f"{entry['score']}"
                time_val = f"{entry['time']}s"
                level = f"L{entry['level']}"
                difficulty = entry['difficulty'][:4]
                
                entry_text = f"{rank:<4} {score:<6} {time_val:<6} {level:<4} {difficulty}"
                text_surface = self.font.render(entry_text, True, colors['text'])
                text_rect = text_surface.get_rect(center=(WIDTH//2, 180 + i * 30))
                self.screen.blit(text_surface, text_rect)
        
        # Back instruction
        back_text = self.font.render("Press ESC to go back", True, colors['accent'])
        back_rect = back_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
        self.screen.blit(back_text, back_rect)
    
    def draw_pause_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        colors = THEME_COLORS[self.theme]
        
        # Animated pause text
        pulse = int(20 * abs(math.sin(time.time() * 2)))
        pause_text = self.big_font.render("PAUSED", True, colors['accent'])
        pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # Controls
        controls = ["P - Resume", "R - Restart", "ESC - Menu"]
        for i, control in enumerate(controls):
            control_text = self.font.render(control, True, colors['text'])
            control_rect = control_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20 + i * 30))
            self.screen.blit(control_text, control_rect)
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        colors = THEME_COLORS[self.theme]
        
        # Game over text with animation
        shake = int(3 * math.sin(time.time() * 10))
        game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
        go_rect = game_over_text.get_rect(center=(WIDTH//2 + shake, HEIGHT//2 - 120))
        self.screen.blit(game_over_text, go_rect)
        
        # New high score check
        if self.score > self.high_score:
            new_hs_text = self.font.render("🎉 NEW HIGH SCORE! 🎉", True, (255, 255, 0))
            hs_rect = new_hs_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
            self.screen.blit(new_hs_text, hs_rect)
        
        # Stats
        time_played = time.time() - self.start_time
        accuracy = (self.hits / max(self.bullets_fired, 1)) * 100
        
        stats = [
            f"Final Score: {self.score}",
            f"High Score: {max(self.score, self.high_score)}",
            f"Time Played: {int(time_played)}s",
            f"Level Reached: {self.level}",
            f"Hits: {self.hits}/{self.bullets_fired}",
            f"Accuracy: {accuracy:.1f}%",
            f"Difficulty: {self.difficulty.name}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, colors['text'])
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40 + i * 25))
            self.screen.blit(text, text_rect)
        
        # Controls
        controls = ["R - Restart", "ESC - Menu"]
        for i, control in enumerate(controls):
            control_text = self.font.render(control, True, colors['accent'])
            control_rect = control_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 140 + i * 25))
            self.screen.blit(control_text, control_rect)
    
    def add_to_leaderboard(self):
        if self.score > 0:
            time_played = time.time() - self.start_time
            accuracy = (self.hits / max(self.bullets_fired, 1)) * 100
            
            entry = {
                'score': self.score,
                'time': int(time_played),
                'accuracy': accuracy,
                'level': self.level,
                'difficulty': self.difficulty.name,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            self.leaderboard.append(entry)
            self.leaderboard.sort(key=lambda x: x['score'], reverse=True)
            self.leaderboard = self.leaderboard[:10]
            self.save_leaderboard()
    
    def reset_game(self):
        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        
        # Add to leaderboard
        self.add_to_leaderboard()
        
        # Reset game state
        self.score = 0
        self.start_time = time.time()
        self.bullets_fired = 0
        self.hits = 0
        self.level = 1
        self.player_x = WIDTH // 2 - 25
        self.bullets = []
        self.obstacles = []
        self.obstacle_timer = 0
        self.alien_speed = 1
        self.alien_direction = 1
        self.paused = False
        self.create_aliens()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:  # Start Game
                            self.reset_game()
                            self.state = "PLAYING"
                        elif self.menu_selection == 1:  # Settings
                            self.state = "SETTINGS"
                        elif self.menu_selection == 2:  # Leaderboard
                            self.state = "LEADERBOARD"
                        elif self.menu_selection == 3:  # Quit
                            return False
            
            elif self.state == "SETTINGS":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.settings_selection = (self.settings_selection - 1) % len(self.settings_options)
                    elif event.key == pygame.K_DOWN:
                        self.settings_selection = (self.settings_selection + 1) % len(self.settings_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT:
                        if self.settings_selection == 0:  # Theme
                            themes = list(Theme)
                            current_idx = themes.index(self.theme)
                            self.theme = themes[(current_idx + 1) % len(themes)]
                            self.graffiti = self.generate_graffiti()  # Update graffiti with new theme
                        elif self.settings_selection == 1:  # Difficulty
                            difficulties = list(Difficulty)
                            current_idx = difficulties.index(self.difficulty)
                            self.difficulty = difficulties[(current_idx + 1) % len(difficulties)]
                        elif self.settings_selection == 2:  # Back
                            self.state = "MENU"
                    elif event.key == pygame.K_LEFT:
                        if self.settings_selection == 0:  # Theme
                            themes = list(Theme)
                            current_idx = themes.index(self.theme)
                            self.theme = themes[(current_idx - 1) % len(themes)]
                            self.graffiti = self.generate_graffiti()
                        elif self.settings_selection == 1:  # Difficulty
                            difficulties = list(Difficulty)
                            current_idx = difficulties.index(self.difficulty)
                            self.difficulty = difficulties[(current_idx - 1) % len(difficulties)]
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
            
            elif self.state == "LEADERBOARD":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
            
            elif self.state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.paused:
                        self.bullets.append([self.player_x + 22, self.player_y])
                        self.bullets_fired += 1
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                        self.state = "PAUSED" if self.paused else "PLAYING"
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
            
            elif self.state == "PAUSED":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = False
                        self.state = "PLAYING"
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        self.state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
            
            elif self.state == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
        
        return True
    
    def update(self):
        if self.state == "PLAYING" and not self.paused:
            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.player_x > 0:
                self.player_x -= self.player_speed
            if keys[pygame.K_RIGHT] and self.player_x < WIDTH - 50:
                self.player_x += self.player_speed
            
            # Update game objects
            self.update_bullets()
            self.update_aliens()
            self.update_obstacles()
            self.check_collisions()
            
            # Check win condition
            if not self.aliens:
                self.level += 1
                self.create_aliens()
                self.alien_speed += 0.3
    
    def draw(self):
        if self.state == "MENU":
            self.draw_menu()
        
        elif self.state == "SETTINGS":
            self.draw_settings()
        
        elif self.state == "LEADERBOARD":
            self.draw_leaderboard()
        
        elif self.state in ["PLAYING", "PAUSED"]:
            colors = THEME_COLORS[self.theme]
            self.screen.fill(colors['bg'])
            
            # Draw graffiti background
            self.draw_graffiti()
            
            # Draw stars
            for i in range(50):
                x = (i * 37) % WIDTH
                y = (i * 23) % HEIGHT
                brightness = 100 + int(50 * math.sin(time.time() + i * 0.1))
                star_color = (brightness, brightness, brightness)
                size = 1 + int(math.sin(time.time() * 2 + i) > 0.7)
                pygame.draw.circle(self.screen, star_color, (x, y), size)
            
            self.draw_player()
            self.draw_aliens()
            self.draw_obstacles()
            self.draw_bullets()
            self.draw_hud()
            
            if self.state == "PAUSED":
                self.draw_pause_screen()
        
        elif self.state == "GAME_OVER":
            colors = THEME_COLORS[self.theme]
            self.screen.fill(colors['bg'])
            self.draw_graffiti()
            
            # Draw stars
            for i in range(50):
                x = (i * 37) % WIDTH
                y = (i * 23) % HEIGHT
                pygame.draw.circle(self.screen, (100, 100, 100), (x, y), 1)
            
            self.draw_player()
            self.draw_aliens()
            self.draw_obstacles()
            self.draw_bullets()
            self.draw_hud()
            self.draw_game_over()
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()