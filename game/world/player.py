import pygame
import math
from game.constants import *


class Player:
    """Игрок на карте."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 32
        self.height = 48
        self.speed = 200

        self.direction = "down"  # up, down, left, right
        self.moving = False
        self.anim_time = 0

        # Цвета персонажа
        self.body_color = (80, 60, 140)
        self.skin_color = (230, 190, 160)
        self.hair_color = (60, 40, 30)
        self.cloak_color = (100, 40, 40)

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def feet_rect(self):
        """Хитбокс для коллизий (только ноги)."""
        return pygame.Rect(int(self.x) + 4, int(self.y) + 32, self.width - 8, 16)

    def handle_input(self, keys_pressed, keybindings):
        """Обработка ввода."""
        self.moving = False
        dx, dy = 0, 0

        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            dy = -1
            self.direction = "up"
            self.moving = True
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            dy = 1
            self.direction = "down"
            self.moving = True
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            dx = -1
            self.direction = "left"
            self.moving = True
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            dx = 1
            self.direction = "right"
            self.moving = True

        # Нормализация диагонального движения
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        return dx, dy

    def update(self, dt, dx, dy, colliders):
        """Обновление позиции с учётом коллизий."""
        if self.moving:
            self.anim_time += dt
        else:
            self.anim_time = 0

        # Движение по X
        new_x = self.x + dx * self.speed * dt
        test_rect = pygame.Rect(int(new_x) + 4, int(self.y) + 32, self.width - 8, 16)
        collision_x = False
        for collider in colliders:
            if test_rect.colliderect(collider):
                collision_x = True
                break
        if not collision_x:
            self.x = new_x

        # Движение по Y
        new_y = self.y + dy * self.speed * dt
        test_rect = pygame.Rect(int(self.x) + 4, int(new_y) + 32, self.width - 8, 16)
        collision_y = False
        for collider in colliders:
            if test_rect.colliderect(collider):
                collision_y = True
                break
        if not collision_y:
            self.y = new_y

    def draw(self, surface, camera_x, camera_y):
        """Отрисовка персонажа."""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)

        # Анимация покачивания при ходьбе
        bob = 0
        if self.moving:
            bob = int(math.sin(self.anim_time * 12) * 2)

        # Тень
        shadow = pygame.Surface((28, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), (0, 0, 28, 10))
        surface.blit(shadow, (screen_x + 2, screen_y + 42))

        # Тело (плащ)
        body_rect = pygame.Rect(screen_x + 4, screen_y + 18 + bob, 24, 28)
        pygame.draw.rect(surface, self.cloak_color, body_rect, border_radius=4)
        pygame.draw.rect(surface, (max(0, self.cloak_color[0] - 30),
                                   max(0, self.cloak_color[1] - 30),
                                   max(0, self.cloak_color[2] - 30)),
                         body_rect, width=1, border_radius=4)

        # Голова
        head_x = screen_x + self.width // 2
        head_y = screen_y + 14 + bob
        pygame.draw.circle(surface, self.skin_color, (head_x, head_y), 10)

        # Волосы
        if self.direction == "down":
            pygame.draw.arc(surface, self.hair_color,
                            (head_x - 10, head_y - 12, 20, 16),
                            0, 3.14, 4)
        elif self.direction == "up":
            pygame.draw.circle(surface, self.hair_color, (head_x, head_y - 2), 10)
        else:
            pygame.draw.arc(surface, self.hair_color,
                            (head_x - 10, head_y - 12, 20, 16),
                            0, 3.14, 4)
            # Боковые волосы
            side = -1 if self.direction == "left" else 1
            pygame.draw.ellipse(surface, self.hair_color,
                                (head_x + side * 6, head_y - 5, 6, 12))

        # Глаза (если смотрит вниз или в стороны)
        if self.direction != "up":
            eye_y = head_y
            if self.direction == "down":
                pygame.draw.circle(surface, (40, 30, 20), (head_x - 4, eye_y), 2)
                pygame.draw.circle(surface, (40, 30, 20), (head_x + 4, eye_y), 2)
            elif self.direction == "left":
                pygame.draw.circle(surface, (40, 30, 20), (head_x - 5, eye_y), 2)
            elif self.direction == "right":
                pygame.draw.circle(surface, (40, 30, 20), (head_x + 5, eye_y), 2)

        # Ноги (анимация ходьбы)
        leg_y = screen_y + 44 + bob
        if self.moving:
            leg_offset = int(math.sin(self.anim_time * 15) * 4)
            pygame.draw.rect(surface, (50, 40, 35),
                             (screen_x + 8, leg_y, 6, 6 - leg_offset // 2), border_radius=2)
            pygame.draw.rect(surface, (50, 40, 35),
                             (screen_x + 18, leg_y, 6, 6 + leg_offset // 2), border_radius=2)
        else:
            pygame.draw.rect(surface, (50, 40, 35),
                             (screen_x + 8, leg_y, 6, 5), border_radius=2)
            pygame.draw.rect(surface, (50, 40, 35),
                             (screen_x + 18, leg_y, 6, 5), border_radius=2)