import pygame
import math
import random
from game.constants import *


def wrap_text(text, font, max_width):
    """Разбивает текст на строки по ширине."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test = current_line + (" " if current_line else "") + word
        if font.size(test)[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines if lines else [""]


class Particle:
    """Частица для эффектов."""

    def __init__(self, x, y, color, velocity, size=4, lifetime=1.0, gravity=0):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-200, 200)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        self.rotation += self.rot_speed * dt
        return self.lifetime > 0

    def draw(self, surface):
        if self.lifetime <= 0:
            return

        alpha = int(255 * (self.lifetime / self.max_lifetime))
        current_size = self.size * (self.lifetime / self.max_lifetime)

        if current_size < 1:
            return

        s = int(current_size)
        particle_surf = pygame.Surface((s * 2 + 2, s * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*self.color[:3], alpha),
                           (s + 1, s + 1), s)
        surface.blit(particle_surf, (int(self.x - s), int(self.y - s)))


class ConfettiParticle(Particle):
    """Конфетти для достижений."""

    COLORS = [
        (255, 100, 100), (100, 255, 100), (100, 100, 255),
        (255, 255, 100), (255, 100, 255), (100, 255, 255),
        (255, 200, 50), (255, 150, 200),
    ]

    def __init__(self, x, y):
        color = random.choice(self.COLORS)
        vx = random.uniform(-180, 180)
        vy = random.uniform(-350, -120)
        size = random.uniform(4, 8)
        super().__init__(x, y, color, (vx, vy),
                         size=size, lifetime=2.2, gravity=450)
        self.shape = random.choice(["square", "circle", "rect"])
        self.w = random.uniform(4, 9)
        self.h = random.uniform(7, 14)

    def draw(self, surface):
        if self.lifetime <= 0:
            return

        life_ratio = self.lifetime / self.max_lifetime
        alpha = int(255 * min(1.0, life_ratio / 0.25))
        scale = min(1.0, life_ratio / 0.4)

        w = max(1, int(self.w * scale))
        h = max(1, int(self.h * scale))

        surf = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)

        if self.shape == "square":
            pygame.draw.rect(surf, (*self.color, alpha), (2, 2, w, h))
        elif self.shape == "circle":
            pygame.draw.ellipse(surf, (*self.color, alpha), (2, 2, w, h))
        else:
            pygame.draw.rect(surf, (*self.color, alpha), (2, 2, w, h // 2))

        rotated = pygame.transform.rotate(surf, self.rotation)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect.topleft)


class Notification:
    """Одно уведомление с анимацией."""

    TYPE_INFO = "info"
    TYPE_SUCCESS = "success"
    TYPE_ACHIEVEMENT = "achievement"
    TYPE_WARNING = "warning"
    TYPE_ERROR = "error"

    COLORS = {
        TYPE_INFO:        (100, 150, 255),
        TYPE_SUCCESS:     (80, 220, 110),
        TYPE_ACHIEVEMENT: (255, 200, 50),
        TYPE_WARNING:     (255, 170, 40),
        TYPE_ERROR:       (255, 80, 80),
    }

    # Максимальная ширина текстовой области
    TEXT_AREA_WIDTH = 230

    def __init__(self, text, notif_type=TYPE_INFO, title=None,
                 duration=4.0, icon_func=None, screen_size=(1280, 720)):
        self.text = text
        self.title = title
        self.notif_type = notif_type
        self.duration = duration
        self.icon_func = icon_func
        self.screen_w, self.screen_h = screen_size
        self.color = self.COLORS.get(notif_type, self.COLORS[self.TYPE_INFO])

        # Шрифты
        self.font_title = pygame.font.SysFont("segoeui", 17, bold=True)
        self.font_text  = pygame.font.SysFont("segoeui", 15)

        # Вычисляем высоту под перенос текста
        self.text_lines = wrap_text(self.text, self.font_text, self.TEXT_AREA_WIDTH)
        line_h = self.font_text.get_linesize()

        if self.title:
            text_block_h = self.font_title.get_linesize() + len(self.text_lines) * line_h + 4
        else:
            text_block_h = len(self.text_lines) * line_h

        self.width  = 360
        self.height = max(72, text_block_h + 30)   # минимум 72px, паддинг 15 сверху+снизу

        # Позиции
        self.x = self.screen_w // 2 - self.width // 2
        self.target_y = self.screen_h - self.height - 30
        self.y = float(self.screen_h + 20)

        # Анимация
        self.state = "entering"
        self.time  = 0.0
        self.alpha = 0
        self.scale = 0.85
        self.glow_pulse = 0.0
        self.shake = 0.0

        # Частицы
        self.particles = []
        if notif_type == self.TYPE_ACHIEVEMENT:
            self._spawn_confetti()

    # ------------------------------------------------------------------
    def _spawn_confetti(self):
        cx = self.screen_w // 2
        cy = self.screen_h - 120
        for _ in range(50):
            self.particles.append(ConfettiParticle(cx, cy))

    def _spawn_burst(self):
        cx = self.x + self.width  // 2
        cy = int(self.y) + self.height // 2
        for _ in range(18):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 180)
            p = Particle(cx, cy, self.color,
                         (math.cos(angle) * speed, math.sin(angle) * speed),
                         size=random.uniform(3, 7),
                         lifetime=0.9, gravity=120)
            self.particles.append(p)

    # ------------------------------------------------------------------
    def update(self, dt):
        self.time += dt
        self.glow_pulse += dt * 3
        self.particles = [p for p in self.particles if p.update(dt)]

        if self.state == "entering":
            progress = min(self.time / 0.45, 1.0)
            eased = 1 - (1 - progress) ** 3          # ease-out cubic

            self.y     = self.screen_h + 20 - (self.screen_h + 20 - self.target_y) * eased
            self.alpha = int(255 * eased)
            self.scale = 0.85 + 0.15 * eased

            if progress >= 1.0:
                self.state = "visible"
                self.time  = 0.0
                self._spawn_burst()
                self.shake = 6.0

        elif self.state == "visible":
            if self.shake > 0:
                self.shake -= dt * 25
                self.shake = max(0.0, self.shake)

            # Плавно двигаемся к target_y (другие уведомления могут его менять)
            self.y += (self.target_y - self.y) * min(dt * 10, 1.0)

            if self.time >= self.duration:
                self.state = "exiting"
                self.time  = 0.0

        elif self.state == "exiting":
            progress = min(self.time / 0.35, 1.0)
            eased = progress ** 2

            self.y     = self.target_y + 60 * eased
            self.alpha = int(255 * (1 - eased))
            self.scale = 1.0 - 0.15 * eased

            if progress >= 1.0:
                self.state = "done"

        return self.state != "done"

    # ------------------------------------------------------------------
    def draw(self, surface):
        if self.alpha <= 0:
            return

        # Частицы
        for p in self.particles:
            p.draw(surface)

        # Тряска
        sx = random.uniform(-self.shake, self.shake) if self.shake > 0.5 else 0
        sy = random.uniform(-self.shake, self.shake) if self.shake > 0.5 else 0

        # Масштабированный прямоугольник
        sw = int(self.width  * self.scale)
        sh = int(self.height * self.scale)
        dx = int(self.x + (self.width  - sw) / 2 + sx)
        dy = int(self.y + (self.height - sh) / 2 + sy)

        # Свечение
        glow_i = 0.5 + 0.35 * math.sin(self.glow_pulse)
        glow_m = 18
        glow_s = pygame.Surface((sw + glow_m * 2, sh + glow_m * 2), pygame.SRCALPHA)
        ga = int(45 * glow_i * (self.alpha / 255))
        pygame.draw.rect(glow_s, (*self.color, ga),
                         (0, 0, sw + glow_m * 2, sh + glow_m * 2), border_radius=16)
        surface.blit(glow_s, (dx - glow_m, dy - glow_m))

        # Фон (градиент)
        bg = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for row in range(sh):
            r_ratio = row / sh
            r = int(18 + r_ratio * 12)
            g = int(15 + r_ratio * 10)
            b = int(32 + r_ratio * 18)
            pygame.draw.line(bg, (r, g, b, min(self.alpha, 245)),
                             (0, row), (sw, row))

        # Маска скругления
        mask = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         (0, 0, sw, sh), border_radius=12)
        bg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Цветная полоса слева
        pygame.draw.rect(bg, (*self.color, self.alpha),
                         (0, 0, 5, sh), border_radius=12)

        # Рамка
        pygame.draw.rect(bg, (*self.color, min(self.alpha, 190)),
                         (0, 0, sw, sh), width=2, border_radius=12)

        surface.blit(bg, (dx, dy))

        # --- Иконка ---
        icon_size = 28
        icon_pad  = 14
        icon_x = dx + icon_pad
        icon_y = dy + sh // 2 - icon_size // 2

        if self.icon_func:
            self.icon_func(surface, icon_x, icon_y, icon_size, self.color)
        else:
            self._draw_default_icon(surface, icon_x, icon_y, icon_size)

        # --- Текст ---
        text_x = icon_x + icon_size + 12
        pad_top = 12
        line_h  = self.font_text.get_linesize()

        if self.title:
            title_s = self.font_title.render(self.title, True, self.color)
            title_s.set_alpha(self.alpha)
            surface.blit(title_s, (text_x, dy + pad_top))
            text_y = dy + pad_top + self.font_title.get_linesize() + 4
        else:
            # Центрируем текст вертикально если нет заголовка
            total_text_h = len(self.text_lines) * line_h
            text_y = dy + sh // 2 - total_text_h // 2

        for line in self.text_lines:
            line_s = self.font_text.render(line, True, COLOR_TEXT)
            line_s.set_alpha(self.alpha)
            surface.blit(line_s, (text_x, text_y))
            text_y += line_h

        # --- Прогресс-бар времени ---
        if self.state == "visible" and self.duration > 0:
            bar_y = dy + sh - 4
            bar_w = sw - 6
            progress = max(0.0, 1.0 - self.time / self.duration)

            pygame.draw.rect(surface, (40, 35, 55),
                             (dx + 3, bar_y, bar_w, 3), border_radius=2)
            if progress > 0:
                pygame.draw.rect(surface, (*self.color, 180),
                                 (dx + 3, bar_y, int(bar_w * progress), 3),
                                 border_radius=2)

    # ------------------------------------------------------------------
    def _draw_default_icon(self, surface, x, y, size):
        color = self.color
        cx = x + size // 2
        cy = y + size // 2
        r  = size // 2 - 2

        if self.notif_type == self.TYPE_SUCCESS:
            pygame.draw.line(surface, color, (cx - 8, cy),     (cx - 2, cy + 7), 3)
            pygame.draw.line(surface, color, (cx - 2, cy + 7), (cx + 9, cy - 6), 3)

        elif self.notif_type == self.TYPE_ACHIEVEMENT:
            pts = []
            for i in range(5):
                a1 = math.radians(-90 + i * 72)
                pts.append((cx + int(r * math.cos(a1)),
                             cy + int(r * math.sin(a1))))
                a2 = math.radians(-90 + i * 72 + 36)
                pts.append((cx + int(r // 2 * math.cos(a2)),
                             cy + int(r // 2 * math.sin(a2))))
            pygame.draw.polygon(surface, color, pts)

        elif self.notif_type == self.TYPE_WARNING:
            pts = [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
            pygame.draw.polygon(surface, color, pts, width=3)
            pygame.draw.line(surface, color, (cx, cy - 3), (cx, cy + 5), 3)
            pygame.draw.circle(surface, color, (cx, cy + 9), 2)

        elif self.notif_type == self.TYPE_ERROR:
            pygame.draw.line(surface, color, (cx - 7, cy - 7), (cx + 7, cy + 7), 3)
            pygame.draw.line(surface, color, (cx + 7, cy - 7), (cx - 7, cy + 7), 3)

        else:  # INFO
            pygame.draw.circle(surface, color, (cx, cy - 7), 3)
            pygame.draw.line(surface, color, (cx, cy - 1), (cx, cy + 9), 3)


# ======================================================================

class NotificationManager:
    """Управляет несколькими уведомлениями."""

    MAX_VISIBLE = 3
    SPACING     = 8

    def __init__(self, screen):
        self.screen        = screen
        self.notifications = []   # активные
        self.queue         = []   # ожидающие

    # --- публичные методы ---

    def show(self, text, notif_type=Notification.TYPE_INFO,
             title=None, duration=4.0, icon_func=None):
        sw, sh = self.screen.get_size()
        n = Notification(text, notif_type, title, duration, icon_func, (sw, sh))
        if len(self.notifications) < self.MAX_VISIBLE:
            self._push(n)
        else:
            self.queue.append(n)

    def show_achievement(self, title, description, icon_func=None):
        self.show(description, Notification.TYPE_ACHIEVEMENT,
                  title=title, duration=5.5, icon_func=icon_func)

    def show_success(self, text, title=None):
        self.show(text, Notification.TYPE_SUCCESS, title=title, duration=3.0)

    def show_warning(self, text, title=None):
        self.show(text, Notification.TYPE_WARNING, title=title, duration=4.0)

    def show_error(self, text, title=None):
        self.show(text, Notification.TYPE_ERROR, title=title, duration=5.0)

    def show_info(self, text, title=None):
        self.show(text, Notification.TYPE_INFO, title=title, duration=4.0)

    # --- внутренние ---

    def _push(self, notif):
        """Добавить уведомление, сдвинув остальные вверх."""
        sh = self.screen.get_height()
        # Пересчитываем target_y для всех существующих
        for existing in self.notifications:
            existing.target_y -= notif.height + self.SPACING
        notif.y        = float(sh + 20)
        notif.target_y = sh - notif.height - 30
        self.notifications.append(notif)

    def update(self, dt):
        self.notifications = [n for n in self.notifications if n.update(dt)]

        # Из очереди
        while self.queue and len(self.notifications) < self.MAX_VISIBLE:
            n = self.queue.pop(0)
            sw, sh = self.screen.get_size()
            n.screen_w, n.screen_h = sw, sh
            n.x        = sw // 2 - n.width // 2
            n.y        = float(sh + 20)
            n.target_y = sh - n.height - 30
            self._push(n)

    def draw(self):
        for n in self.notifications:
            n.draw(self.screen)