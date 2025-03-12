# made by @kotokk
# requires pygame and (optional) dateutil
import pygame
import random
import math
import colorsys
import datetime
import sys

try:
    from dateutil.relativedelta import relativedelta
    use_relativedelta = True
except ImportError:
    use_relativedelta = False

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

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.phase = random.uniform(0, 2 * math.pi)
    def update(self):
        self.phase += 0.02
    def draw(self, surface):
        alpha = 128 + int(127 * (math.sin(self.phase) + 1) / 2)
        star_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (255, 255, 255, alpha), (self.size, self.size), self.size)
        surface.blit(star_surf, (self.x, self.y))

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
        glow_surf = pygame.Surface((self.size * 6, self.size * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, self.color + (max(0, alpha // 2),), (self.size * 3, self.size * 3), self.size * 3)
        surface.blit(glow_surf, (int(self.x - self.size * 3), int(self.y - self.size * 3)))
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, self.color + (alpha,), (self.size, self.size), self.size)
        surface.blit(particle_surf, (int(self.x - self.size), int(self.y - self.size)))
    def is_dead(self):
        return self.age >= self.lifetime

pygame.font.init()
timer_font = pygame.font.SysFont("Arial", 64)
message_font = pygame.font.SysFont("Arial", 96)
close_font = pygame.font.SysFont("Arial", 24)
close_button_rect = pygame.Rect(WIDTH - 50 if not sys.platform.startswith("darwin") else 10, 10, 40, 40)
stars = [Star() for _ in range(100)]
rockets = []
rocket_timer = 0
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
    for star in stars:
        star.update()
        star.draw(screen)
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
    target = datetime.datetime(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0)
    if now < target:
        if use_relativedelta:
            rd = relativedelta(target, now)
            countdown_text = f"{rd.months} months, {rd.days} days, {rd.hours:02d}:{rd.minutes:02d}:{rd.seconds:02d}"
        else:
            diff = target - now
            total_seconds = int(diff.total_seconds())
            days = total_seconds // 86400
            months = days // 30
            days = days % 30
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            countdown_text = f"{months} months, {days} days, {hours:02d}:{minutes:02d}:{seconds:02d}"
        timer_surface = timer_font.render(countdown_text, True, (255, 255, 255))
        timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 50))
        screen.blit(timer_surface, timer_rect)
    else:
        scale = 1 + 0.1 * math.sin(pygame.time.get_ticks() / 200.0)
        msg = "Happy New Year!"
        message_surface = message_font.render(msg, True, (255, 255, 255))
        new_size = (int(message_surface.get_width() * scale), int(message_surface.get_height() * scale))
        message_surface = pygame.transform.scale(message_surface, new_size)
        message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(message_surface, message_rect)
    pygame.draw.rect(screen, (200, 50, 50), close_button_rect)
    close_text_surface = close_font.render("X", True, (255, 255, 255))
    close_text_rect = close_text_surface.get_rect(center=close_button_rect.center)
    screen.blit(close_text_surface, close_text_rect)
    pygame.display.flip()
pygame.quit()
