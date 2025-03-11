import pygame
import random
import math
import colorsys
import datetime
import sys

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
pygame.display.set_caption("New Year Fireworks Visualiser")
clock = pygame.time.Clock()
GRAVITY = 0.1
WIND = 0.0

def random_color():
    hue = random.random()
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    return (int(r * 255), int(g * 255), int(b * 255))

class Rocket:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = int(HEIGHT * 0.95)
        self.vx = 0
        self.vy = random.uniform(-12, -10)
        self.color = random_color()
        self.exploded = False
        self.trail = []
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:
            self.trail.pop(0)
        self.x += self.vx + WIND
        self.y += self.vy
        self.vy += GRAVITY
        if self.vy >= 0:
            self.explode()
    def explode(self):
        self.exploded = True
        num_particles = random.randint(80, 150)
        self.particles = []
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            self.particles.append(Particle(self.x, self.y, vx, vy, self.color))
    def draw(self, surface):
        if not self.exploded:
            for i in range(1, len(self.trail)):
                alpha = int(255 * (i / len(self.trail)))
                trail_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, self.color + (alpha,), (2, 2), 2)
                pos = self.trail[i]
                surface.blit(trail_surf, (int(pos[0] - 2), int(pos[1] - 2)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)
        else:
            for p in self.particles:
                p.draw(surface)
    def update_particles(self):
        if self.exploded:
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if not p.is_dead()]
    def is_dead(self):
        return self.exploded and len(self.particles) == 0

class Particle:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = random.randint(50, 100)
        self.age = 0
        self.trail = []
        self.size = random.randint(2, 4)
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        self.x += self.vx + WIND
        self.y += self.vy
        self.vy += GRAVITY * 0.5
        self.vx *= 0.98
        self.vy *= 0.98
        self.age += 1
    def draw(self, surface):
        if len(self.trail) > 1:
            for idx, pos in enumerate(self.trail):
                alpha = int(255 * (idx / len(self.trail)))
                trail_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, self.color + (alpha,), (self.size, self.size), self.size)
                surface.blit(trail_surf, (int(pos[0] - self.size), int(pos[1] - self.size)))
        alpha = max(0, 255 - int(255 * (self.age / self.lifetime)))
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, self.color + (alpha,), (self.size, self.size), self.size)
        surface.blit(particle_surf, (int(self.x - self.size), int(self.y - self.size)))
    def is_dead(self):
        return self.age >= self.lifetime

rockets = []
rocket_timer = 0
pygame.font.init()
timer_font = pygame.font.SysFont("Arial", 64)
message_font = pygame.font.SysFont("Arial", 96)
close_font = pygame.font.SysFont("Arial", 24)
close_button_rect = pygame.Rect(WIDTH - 50 if not sys.platform.startswith("darwin") else 10, 10, 40, 40)
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if close_button_rect.collidepoint(event.pos):
                running = False
    screen.fill((0, 0, 0))
    if rocket_timer <= 0:
        rockets.append(Rocket())
        rocket_timer = random.randint(20, 50)
    else:
        rocket_timer -= 1
    for rocket in rockets:
        if not rocket.exploded:
            rocket.update()
        else:
            rocket.update_particles()
        rocket.draw(screen)
    rockets = [r for r in rockets if not r.is_dead()]
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    midnight = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=0, minute=0, second=0)
    diff = midnight - now
    if diff.total_seconds() > 0:
        total_seconds = int(diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        timer_surface = timer_font.render(timer_text, True, (255, 255, 255))
        timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 50))
        screen.blit(timer_surface, timer_rect)
    else:
        message_surface = message_font.render("Happy New Year!", True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(WIDTH // 2, 50))
        screen.blit(message_surface, message_rect)
    pygame.draw.rect(screen, (200, 50, 50), close_button_rect)
    close_text_surface = close_font.render("X", True, (255, 255, 255))
    close_text_rect = close_text_surface.get_rect(center=close_button_rect.center)
    screen.blit(close_text_surface, close_text_rect)
    pygame.display.flip()
pygame.quit()