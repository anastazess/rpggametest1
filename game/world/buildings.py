import pygame
from game.constants import *


class Building:
    """Базовый класс здания."""

    def __init__(self, x, y, width, height, name,
                 color=(80, 70, 100), roof_color=(120, 60, 60)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.color = color
        self.roof_color = roof_color
        self.hovered = False
        self.interaction_rect = pygame.Rect(x, y + height - 40, width, 50)

        self.font = pygame.font.SysFont("segoeui", 14, bold=True)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def collision_rect(self):
        """Область коллизии (нижняя часть здания)."""
        return pygame.Rect(self.x, self.y + self.height - 30,
                           self.width, 30)

    def update(self, player_rect):
        self.hovered = self.interaction_rect.colliderect(player_rect)

    def draw(self, surface, camera_x, camera_y):
        sx = self.x - camera_x
        sy = self.y - camera_y

        # Тень здания
        shadow = pygame.Surface((self.width + 10, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 40),
                            (0, 0, self.width + 10, 20))
        surface.blit(shadow, (sx - 5, sy + self.height - 5))

        # Стены
        wall_rect = pygame.Rect(sx, sy + 30, self.width, self.height - 30)
        pygame.draw.rect(surface, self.color, wall_rect)
        pygame.draw.rect(surface, tuple(max(0, c - 30) for c in self.color),
                         wall_rect, width=2)

        # Крыша
        roof_points = [
            (sx - 10, sy + 35),
            (sx + self.width // 2, sy),
            (sx + self.width + 10, sy + 35),
        ]
        pygame.draw.polygon(surface, self.roof_color, roof_points)
        pygame.draw.polygon(surface, tuple(max(0, c - 40) for c in self.roof_color),
                            roof_points, width=2)

        # Дверь
        door_w = 30
        door_h = 50
        door_x = sx + self.width // 2 - door_w // 2
        door_y = sy + self.height - door_h
        pygame.draw.rect(surface, (50, 35, 25),
                         (door_x, door_y, door_w, door_h), border_radius=3)
        pygame.draw.rect(surface, (35, 25, 15),
                         (door_x, door_y, door_w, door_h), width=2, border_radius=3)
        # Ручка
        pygame.draw.circle(surface, (180, 150, 50),
                           (door_x + door_w - 8, door_y + door_h // 2), 3)

        # Окна
        win_size = 20
        win_y = sy + 50
        for wx in [sx + 15, sx + self.width - 35]:
            pygame.draw.rect(surface, (200, 220, 255),
                             (wx, win_y, win_size, win_size))
            pygame.draw.rect(surface, (40, 30, 25),
                             (wx, win_y, win_size, win_size), width=2)
            # Перекладины
            pygame.draw.line(surface, (40, 30, 25),
                             (wx + win_size // 2, win_y),
                             (wx + win_size // 2, win_y + win_size), 2)
            pygame.draw.line(surface, (40, 30, 25),
                             (wx, win_y + win_size // 2),
                             (wx + win_size, win_y + win_size // 2), 2)

        # Подсветка при наведении
        if self.hovered:
            # Рамка взаимодействия
            interact_surf = pygame.Surface((self.width + 20, 60), pygame.SRCALPHA)
            pygame.draw.rect(interact_surf, (*COLOR_ACCENT[:3], 40),
                             (0, 0, self.width + 20, 60), border_radius=8)
            pygame.draw.rect(interact_surf, (*COLOR_ACCENT[:3], 150),
                             (0, 0, self.width + 20, 60), width=2, border_radius=8)
            surface.blit(interact_surf, (sx - 10, sy + self.height - 45))

            # Подсказка
            hint = f"[E] Войти в {self.name}"
            hint_surf = self.font.render(hint, True, COLOR_ACCENT)
            hint_x = sx + self.width // 2 - hint_surf.get_width() // 2
            hint_y = sy - 25

            # Фон подсказки
            hint_bg = pygame.Surface((hint_surf.get_width() + 16, 24), pygame.SRCALPHA)
            pygame.draw.rect(hint_bg, (20, 15, 35, 220),
                             (0, 0, hint_bg.get_width(), 24), border_radius=5)
            surface.blit(hint_bg, (hint_x - 8, hint_y - 3))
            surface.blit(hint_surf, (hint_x, hint_y))


class GuildBuilding(Building):
    """Здание гильдии."""

    def __init__(self, x, y):
        super().__init__(x, y, 120, 100, "Гильдию",
                         color=(70, 65, 95), roof_color=(100, 50, 50))

    def draw(self, surface, camera_x, camera_y):
        super().draw(surface, camera_x, camera_y)

        sx = self.x - camera_x
        sy = self.y - camera_y

        # Вывеска
        sign_w = 80
        sign_h = 20
        sign_x = sx + self.width // 2 - sign_w // 2
        sign_y = sy + 25

        pygame.draw.rect(surface, (60, 45, 30),
                         (sign_x, sign_y, sign_w, sign_h), border_radius=3)
        pygame.draw.rect(surface, (40, 30, 20),
                         (sign_x, sign_y, sign_w, sign_h), width=1, border_radius=3)

        font = pygame.font.SysFont("segoeui", 12, bold=True)
        text = font.render("ГИЛЬДИЯ", True, (220, 200, 150))
        surface.blit(text, (sign_x + sign_w // 2 - text.get_width() // 2,
                            sign_y + 3))


class ShopBuilding(Building):
    """Магазин."""

    def __init__(self, x, y):
        super().__init__(x, y, 100, 90, "Магазин",
                         color=(85, 75, 65), roof_color=(60, 100, 60))

    def draw(self, surface, camera_x, camera_y):
        super().draw(surface, camera_x, camera_y)

        sx = self.x - camera_x
        sy = self.y - camera_y

        # Вывеска с зельем
        sign_x = sx + self.width // 2
        sign_y = sy + 20

        # Бутылка
        pygame.draw.ellipse(surface, (100, 200, 100),
                            (sign_x - 8, sign_y, 16, 20))
        pygame.draw.rect(surface, (100, 200, 100),
                         (sign_x - 4, sign_y - 6, 8, 8))


class TavernBuilding(Building):
    """Таверна."""

    def __init__(self, x, y):
        super().__init__(x, y, 130, 95, "Таверну",
                         color=(90, 70, 55), roof_color=(80, 60, 40))

    def draw(self, surface, camera_x, camera_y):
        super().draw(surface, camera_x, camera_y)

        sx = self.x - camera_x
        sy = self.y - camera_y

        # Вывеска с кружкой
        sign_x = sx + self.width // 2 - 10
        sign_y = sy + 18

        pygame.draw.rect(surface, (200, 180, 100),
                         (sign_x, sign_y, 15, 18), border_radius=2)
        pygame.draw.arc(surface, (200, 180, 100),
                        (sign_x + 12, sign_y + 3, 10, 12),
                        -1.5, 1.5, 3)


class TempleBuilding(Building):
    """Величественный храм Богини Авэлин."""

    def __init__(self, x, y):
        # Большое здание
        super().__init__(x, y, 200, 160, "Храм",
                         color=(100, 95, 125), roof_color=(130, 115, 155))

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        # Большая тень
        shadow = pygame.Surface((self.width + 20, 25), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 45), (0, 0, self.width + 20, 25))
        surface.blit(shadow, (sx - 10, sy + self.height - 8))

        # Ступени (три уровня)
        for step in range(3):
            step_w = self.width + 20 - step * 10
            step_h = 8
            step_x = sx - 10 + step * 5
            step_y = sy + self.height - 15 + step * 5
            pygame.draw.rect(surface, (150, 140, 160),
                             (step_x, step_y, step_w, step_h))
            pygame.draw.rect(surface, (120, 110, 130),
                             (step_x, step_y, step_w, step_h), width=1)

        # Основание храма (более высокое)
        base_rect = pygame.Rect(sx, sy + 50, self.width, self.height - 50)
        pygame.draw.rect(surface, self.color, base_rect)
        pygame.draw.rect(surface, tuple(max(0, c - 25) for c in self.color),
                         base_rect, width=2)

        # Колонны (6 штук)
        col_positions = [15, 45, 75, 125, 155, 185]
        for i, col_x in enumerate(col_positions):
            # Тень колонны
            pygame.draw.rect(surface, tuple(max(0, c - 20) for c in self.color),
                             (sx + col_x + 3, sy + 55, 14, self.height - 80))
            # Колонна
            pygame.draw.rect(surface, (175, 165, 190),
                             (sx + col_x, sy + 52, 12, self.height - 75))
            # Капитель (верх)
            pygame.draw.rect(surface, (190, 180, 205),
                             (sx + col_x - 3, sy + 48, 18, 8))
            # База (низ)
            pygame.draw.rect(surface, (160, 150, 175),
                             (sx + col_x - 2, sy + self.height - 25, 16, 6))

        # Крыша — треугольный фронтон
        roof_points = [
            (sx - 15, sy + 55),
            (sx + self.width // 2, sy),
            (sx + self.width + 15, sy + 55),
        ]
        pygame.draw.polygon(surface, self.roof_color, roof_points)
        pygame.draw.polygon(surface, tuple(max(0, c - 30) for c in self.roof_color),
                            roof_points, width=2)

        # Внутренний треугольник (тимпан)
        inner_points = [
            (sx + 15, sy + 50),
            (sx + self.width // 2, sy + 12),
            (sx + self.width - 15, sy + 50),
        ]
        pygame.draw.polygon(surface, tuple(max(0, c - 15) for c in self.roof_color),
                            inner_points)

        # Звезда богини на фронтоне
        import math
        star_cx = sx + self.width // 2
        star_cy = sy + 32
        star_points = []
        for i in range(5):
            # Внешние лучи
            angle = math.radians(-90 + i * 72)
            ox = star_cx + int(14 * math.cos(angle))
            oy = star_cy + int(14 * math.sin(angle))
            star_points.append((ox, oy))
            # Внутренние точки
            angle2 = math.radians(-90 + i * 72 + 36)
            ix = star_cx + int(6 * math.cos(angle2))
            iy = star_cy + int(6 * math.sin(angle2))
            star_points.append((ix, iy))
        pygame.draw.polygon(surface, (255, 230, 180), star_points)
        pygame.draw.polygon(surface, (220, 190, 130), star_points, width=1)

        # Свечение вокруг звезды
        glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 200, 40), (20, 20), 18)
        surface.blit(glow, (star_cx - 20, star_cy - 20))

        # Дверь (большая двойная)
        door_w = 50
        door_h = 70
        door_x = sx + self.width // 2 - door_w // 2
        door_y = sy + self.height - door_h - 10

        # Арка над дверью
        pygame.draw.arc(surface, (140, 130, 155),
                        (door_x - 5, door_y - 15, door_w + 10, 30),
                        0, math.pi, 4)

        # Левая створка
        pygame.draw.rect(surface, (70, 55, 50),
                         (door_x, door_y, door_w // 2 - 2, door_h),
                         border_radius=0)
        # Правая створка
        pygame.draw.rect(surface, (65, 50, 45),
                         (door_x + door_w // 2 + 2, door_y, door_w // 2 - 2, door_h),
                         border_radius=0)
        # Рамка
        pygame.draw.rect(surface, (50, 40, 35),
                         (door_x - 3, door_y - 3, door_w + 6, door_h + 6),
                         width=3, border_radius=2)

        # Ручки дверей
        pygame.draw.circle(surface, (200, 180, 100),
                           (door_x + door_w // 2 - 8, door_y + door_h // 2), 4)
        pygame.draw.circle(surface, (200, 180, 100),
                           (door_x + door_w // 2 + 8, door_y + door_h // 2), 4)

        # Витражные окна (круглые, по бокам)
        for win_x in [sx + 30, sx + self.width - 50]:
            # Рамка окна
            pygame.draw.circle(surface, (60, 50, 55), (win_x + 10, sy + 85), 16, 3)
            # Цветное стекло
            pygame.draw.circle(surface, (180, 140, 200), (win_x + 10, sy + 85), 12)
            pygame.draw.circle(surface, (200, 160, 220), (win_x + 10, sy + 82), 6)
            # Блик
            pygame.draw.circle(surface, (255, 240, 255, 150), (win_x + 6, sy + 81), 3)

        # Вывеска
        font = pygame.font.SysFont("georgia", 11, bold=True)
        text = font.render("ХРАМ АВЭЛИН", True, (240, 220, 255))
        text_bg = pygame.Surface((text.get_width() + 14, text.get_height() + 6),
                                 pygame.SRCALPHA)
        pygame.draw.rect(text_bg, (60, 50, 80, 200),
                         text_bg.get_rect(), border_radius=4)
        surface.blit(text_bg, (sx + self.width // 2 - text_bg.get_width() // 2,
                               sy + self.height - 95))
        surface.blit(text, (sx + self.width // 2 - text.get_width() // 2,
                            sy + self.height - 92))

        # Подсветка при наведении
        if self.hovered:
            hint_rect = pygame.Rect(sx - 10, sy + self.height - 40,
                                    self.width + 20, 50)
            hint_surf = pygame.Surface((hint_rect.width, hint_rect.height),
                                       pygame.SRCALPHA)
            pygame.draw.rect(hint_surf, (*COLOR_ACCENT[:3], 35),
                             (0, 0, hint_rect.width, hint_rect.height),
                             border_radius=8)
            pygame.draw.rect(hint_surf, (*COLOR_ACCENT[:3], 140),
                             (0, 0, hint_rect.width, hint_rect.height),
                             width=2, border_radius=8)
            surface.blit(hint_surf, hint_rect.topleft)

            hint_font = pygame.font.SysFont("segoeui", 13, bold=True)
            hint = f"[E] Войти в {self.name}"
            hint_s = hint_font.render(hint, True, COLOR_ACCENT)
            hint_x = sx + self.width // 2 - hint_s.get_width() // 2
            surface.blit(hint_s, (hint_x, sy - 22))

class BlacksmithBuilding(Building):
    """Кузница."""

    def __init__(self, x, y):
        super().__init__(x, y, 110, 95, "Кузницу",
                         color=(60, 55, 55), roof_color=(50, 45, 45))

    def draw(self, surface, camera_x, camera_y):
        super().draw(surface, camera_x, camera_y)

        sx = self.x - camera_x
        sy = self.y - camera_y

        # Наковальня на вывеске
        anvil_x = sx + self.width // 2 - 12
        anvil_y = sy + 20

        pygame.draw.rect(surface, (100, 100, 110),
                         (anvil_x, anvil_y + 5, 24, 8))
        pygame.draw.rect(surface, (100, 100, 110),
                         (anvil_x + 8, anvil_y, 8, 15))

        # Дым из трубы
        import random
        chimney_x = sx + self.width - 25
        chimney_y = sy + 5
        for i in range(3):
            smoke_y = chimney_y - i * 8 - random.randint(0, 3)
            smoke_size = 6 + i * 2
            smoke_alpha = 80 - i * 20
            smoke = pygame.Surface((smoke_size * 2, smoke_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(smoke, (150, 150, 150, smoke_alpha),
                               (smoke_size, smoke_size), smoke_size)
            surface.blit(smoke, (chimney_x - smoke_size + i * 3, smoke_y - smoke_size))