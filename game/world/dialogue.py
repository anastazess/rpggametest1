import pygame
import math
from game.constants import *


class DialogueBox:
    """Диалоговое окно с аватаром персонажа."""

    def __init__(self, screen):
        self.screen = screen
        self.active = False
        self.dialogues = []
        self.current_index = 0
        self.char_index = 0
        self.char_timer = 0.0
        self.char_speed = 0.025
        self.finished_typing = False
        self.time = 0.0

        self.font_name = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_text = pygame.font.SysFont("segoeui", 17)
        self.font_hint = pygame.font.SysFont("segoeui", 13)

        self._calculate_layout()

    def _calculate_layout(self):
        sw, sh = self.screen.get_size()
        self.box_w = min(750, sw - 60)
        self.box_h = 170
        self.box_x = sw // 2 - self.box_w // 2
        self.box_y = sh - self.box_h - 25
        self.box_rect = pygame.Rect(self.box_x, self.box_y, self.box_w, self.box_h)

        # Размер аватара
        self.avatar_size = 100
        self.avatar_x = self.box_x + 20
        self.avatar_y = self.box_y + self.box_h // 2 - self.avatar_size // 2

    def start_dialogue(self, dialogues):
        """
        dialogues: список словарей
        [
            {
                "speaker": "Имя",
                "text": "Текст",
                "portrait_color": (r, g, b),
                "appearance": NPCAppearance (опционально)
            },
            ...
        ]
        """
        self.dialogues = dialogues
        self.current_index = 0
        self.char_index = 0
        self.char_timer = 0.0
        self.finished_typing = False
        self.active = True
        self._calculate_layout()

    def update(self, dt):
        if not self.active or not self.dialogues:
            return

        self.time += dt
        current = self.dialogues[self.current_index]
        full_text = current["text"]

        if self.char_index < len(full_text):
            self.char_timer += dt
            while self.char_timer >= self.char_speed and self.char_index < len(full_text):
                self.char_timer -= self.char_speed
                self.char_index += 1
        else:
            self.finished_typing = True

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                if self.finished_typing:
                    self.current_index += 1
                    if self.current_index >= len(self.dialogues):
                        self.active = False
                        return True
                    self.char_index = 0
                    self.char_timer = 0.0
                    self.finished_typing = False
                else:
                    self.char_index = len(self.dialogues[self.current_index]["text"])
                    self.finished_typing = True
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.box_rect.collidepoint(event.pos):
                if self.finished_typing:
                    self.current_index += 1
                    if self.current_index >= len(self.dialogues):
                        self.active = False
                        return True
                    self.char_index = 0
                    self.char_timer = 0.0
                    self.finished_typing = False
                else:
                    self.char_index = len(self.dialogues[self.current_index]["text"])
                    self.finished_typing = True
                return True

        return False

    def draw(self):
        if not self.active or not self.dialogues:
            return

        current = self.dialogues[self.current_index]

        # Затемнение фона
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        self.screen.blit(overlay, (0, 0))

        # Основной бокс
        self._draw_box()

        # Аватар
        self._draw_avatar(current)

        # Имя и текст
        self._draw_text(current)

        # Индикаторы
        self._draw_indicators()

    def _draw_box(self):
        """Рисуем фон диалогового окна."""
        box = pygame.Surface((self.box_w, self.box_h), pygame.SRCALPHA)

        # Градиент
        for row in range(self.box_h):
            ratio = row / self.box_h
            r = int(18 + ratio * 12)
            g = int(15 + ratio * 10)
            b = int(35 + ratio * 18)
            pygame.draw.line(box, (r, g, b, 245), (0, row), (self.box_w, row))

        # Скругление
        mask = pygame.Surface((self.box_w, self.box_h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                        (0, 0, self.box_w, self.box_h), border_radius=14)
        box.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Рамка
        pygame.draw.rect(box, (*COLOR_PRIMARY_DARK, 200),
                        (0, 0, self.box_w, self.box_h), width=2, border_radius=14)

        # Декоративная линия
        pygame.draw.line(box, (*COLOR_PRIMARY_DARK, 100),
                        (self.avatar_size + 35, 15),
                        (self.avatar_size + 35, self.box_h - 15), 1)

        self.screen.blit(box, (self.box_x, self.box_y))

    def _draw_avatar(self, dialogue_data):
        """Рисуем аватар персонажа."""
        portrait_color = dialogue_data.get("portrait_color", (150, 130, 170))
        appearance = dialogue_data.get("appearance", None)

        ax = self.avatar_x
        ay = self.avatar_y
        size = self.avatar_size

        # Фон аватара
        avatar_bg = pygame.Surface((size + 8, size + 8), pygame.SRCALPHA)
        pygame.draw.rect(avatar_bg, (25, 22, 40, 230),
                        (0, 0, size + 8, size + 8), border_radius=10)
        pygame.draw.rect(avatar_bg, (*portrait_color, 180),
                        (0, 0, size + 8, size + 8), width=2, border_radius=10)
        self.screen.blit(avatar_bg, (ax - 4, ay - 4))

        # Внутренний фон (градиент)
        inner = pygame.Surface((size, size), pygame.SRCALPHA)
        for row in range(size):
            ratio = row / size
            r = int(portrait_color[0] * 0.15 + ratio * 10)
            g = int(portrait_color[1] * 0.15 + ratio * 8)
            b = int(portrait_color[2] * 0.15 + ratio * 12)
            pygame.draw.line(inner, (r, g, b, 200), (0, row), (size, row))
        self.screen.blit(inner, (ax, ay))

        # Рисуем персонажа
        if appearance:
            self._draw_character_avatar(ax, ay, size, appearance, portrait_color)
        else:
            self._draw_simple_avatar(ax, ay, size, portrait_color)

        # Свечение вокруг аватара
        glow = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
        glow_alpha = int(30 + math.sin(self.time * 2) * 10)
        pygame.draw.rect(glow, (*portrait_color, glow_alpha),
                        (0, 0, size + 20, size + 20), border_radius=14)
        self.screen.blit(glow, (ax - 10, ay - 10))

    def _draw_simple_avatar(self, ax, ay, size, color):
        """Простой аватар (силуэт) когда нет данных о внешности."""
        cx = ax + size // 2
        cy = ay + size // 2

        # Тело
        body_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.ellipse(self.screen, body_color,
                          (cx - 25, cy + 10, 50, 40))

        # Голова
        head_color = (225, 190, 165)
        pygame.draw.circle(self.screen, head_color, (cx, cy - 5), 22)

        # Волосы (простые)
        hair_color = tuple(max(0, c - 60) for c in color)
        pygame.draw.arc(self.screen, hair_color,
                       (cx - 22, cy - 30, 44, 35), 0, math.pi, 6)

        # Глаза
        pygame.draw.circle(self.screen, (50, 40, 35), (cx - 8, cy - 5), 3)
        pygame.draw.circle(self.screen, (50, 40, 35), (cx + 8, cy - 5), 3)
        # Блики
        pygame.draw.circle(self.screen, (255, 255, 255), (cx - 7, cy - 6), 1)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx + 9, cy - 6), 1)

        # Рот (лёгкая улыбка)
        pygame.draw.arc(self.screen, (180, 120, 100),
                       (cx - 6, cy + 2, 12, 8), 3.14, 6.28, 2)

    def _draw_character_avatar(self, ax, ay, size, appearance, base_color):
        """Детализированный аватар с учётом внешности NPC."""
        cx = ax + size // 2
        cy = ay + size // 2 + 5

        a = appearance

        # ═══════════════════════════════════════════════════════════════
        # ТЕЛО / ОДЕЖДА
        # ═══════════════════════════════════════════════════════════════

        body_w = 55
        body_h = 45

        # Тень тела
        pygame.draw.ellipse(self.screen, tuple(max(0, c - 30) for c in a.outfit_color),
                          (cx - body_w // 2 + 3, cy + 13, body_w, body_h))

        # Основное тело/одежда
        pygame.draw.ellipse(self.screen, a.outfit_color,
                          (cx - body_w // 2, cy + 10, body_w, body_h))

        # Воротник / детали одежды
        collar_color = tuple(min(255, c + 25) for c in a.outfit_color)
        pygame.draw.arc(self.screen, collar_color,
                       (cx - 15, cy + 5, 30, 20), 0, math.pi, 3)

        # Фартук
        if a.accessory == "apron":
            pygame.draw.rect(self.screen, (235, 225, 210),
                           (cx - 18, cy + 18, 36, 30), border_radius=3)
            pygame.draw.rect(self.screen, (220, 210, 195),
                           (cx - 18, cy + 18, 36, 30), width=1, border_radius=3)

        # Капюшон
        if a.accessory == "hood":
            hood_color = tuple(max(0, c - 15) for c in a.outfit_color)
            pygame.draw.ellipse(self.screen, hood_color,
                              (cx - 28, cy - 30, 56, 45))
            pygame.draw.ellipse(self.screen, a.outfit_color,
                              (cx - 24, cy - 25, 48, 38))

        # Плащ
        if a.accessory == "cape":
            cape_color = tuple(max(0, c - 20) for c in a.outfit_color)
            pygame.draw.polygon(self.screen, cape_color, [
                (cx - 30, cy + 5),
                (cx + 30, cy + 5),
                (cx + 35, cy + 50),
                (cx - 35, cy + 50),
            ])

        # ═══════════════════════════════════════════════════════════════
        # ГОЛОВА
        # ═══════════════════════════════════════════════════════════════

        head_radius = 26
        head_y = cy - 12

        # Тень головы
        pygame.draw.circle(self.screen, tuple(max(0, c - 30) for c in a.skin_color),
                         (cx + 2, head_y + 2), head_radius)

        # Голова
        pygame.draw.circle(self.screen, a.skin_color, (cx, head_y), head_radius)

        # Румянец
        blush = tuple(min(255, c + 20) if i == 0 else max(0, c - 10)
                     for i, c in enumerate(a.skin_color))
        pygame.draw.circle(self.screen, blush, (cx - 16, head_y + 8), 6)
        pygame.draw.circle(self.screen, blush, (cx + 16, head_y + 8), 6)

        # ═══════════════════════════════════════════════════════════════
        # ВОЛОСЫ
        # ═══════════════════════════════════════════════════════════════

        hair_col = a.hair_color

        if a.hair_style == "short":
            # Короткие волосы
            pygame.draw.arc(self.screen, hair_col,
                          (cx - head_radius - 2, head_y - head_radius - 5,
                           head_radius * 2 + 4, head_radius + 10),
                          0, math.pi, 8)
            # Чёлка
            pygame.draw.ellipse(self.screen, hair_col,
                              (cx - 18, head_y - head_radius + 2, 36, 18))

        elif a.hair_style == "long":
            # Длинные волосы
            pygame.draw.arc(self.screen, hair_col,
                          (cx - head_radius - 2, head_y - head_radius - 5,
                           head_radius * 2 + 4, head_radius + 10),
                          0, math.pi, 8)
            # Боковые пряди
            pygame.draw.ellipse(self.screen, hair_col,
                              (cx - head_radius - 8, head_y - 10, 16, 50))
            pygame.draw.ellipse(self.screen, hair_col,
                              (cx + head_radius - 8, head_y - 10, 16, 50))
            # Чёлка
            pygame.draw.ellipse(self.screen, hair_col,
                              (cx - 18, head_y - head_radius + 2, 36, 18))

        elif a.hair_style == "ponytail":
            # Хвост
            pygame.draw.arc(self.screen, hair_col,
                          (cx - head_radius - 2, head_y - head_radius - 5,
                           head_radius * 2 + 4, head_radius + 10),
                          0, math.pi, 8)
            # Хвостик сверху
            pygame.draw.ellipse(self.screen, hair_col,
                              (cx - 6, head_y - head_radius - 15, 12, 20))
            # Резинка
            pygame.draw.ellipse(self.screen, tuple(max(0, c - 30) for c in hair_col),
                              (cx - 4, head_y - head_radius - 2, 8, 6))
            # Чёлка
            pygame.draw.ellipse(self.screen, hair_col,
                              (cx - 15, head_y - head_radius + 3, 30, 14))

        elif a.hair_style == "bald":
            # Лысый — ничего не рисуем, только блик на голове
            pygame.draw.ellipse(self.screen, tuple(min(255, c + 30) for c in a.skin_color),
                              (cx - 8, head_y - head_radius + 5, 16, 10))

        # ═══════════════════════════════════════════════════════════════
        # БОРОДА
        # ═══════════════════════════════════════════════════════════════

        if a.has_beard:
            beard_color = hair_col
            pygame.draw.ellipse(self.screen, beard_color,
                              (cx - 14, head_y + 8, 28, 25))
            pygame.draw.ellipse(self.screen, beard_color,
                              (cx - 10, head_y + 15, 20, 18))

        # ═══════════════════════════════════════════════════════════════
        # ШЛЯПА
        # ═══════════════════════════════════════════════════════════════

        if a.has_hat:
            hat_y = head_y - head_radius - 3
            hat_col = a.hat_color

            # Поля шляпы
            pygame.draw.ellipse(self.screen, hat_col,
                              (cx - 28, hat_y, 56, 14))
            # Тулья
            pygame.draw.rect(self.screen, hat_col,
                           (cx - 16, hat_y - 18, 32, 22), border_radius=5)
            # Лента
            pygame.draw.rect(self.screen, tuple(max(0, c - 30) for c in hat_col),
                           (cx - 16, hat_y - 5, 32, 5))

        # ═══════════════════════════════════════════════════════════════
        # ЛИЦО
        # ═══════════════════════════════════════════════════════════════

        # Глаза
        eye_y = head_y - 2
        eye_color = (55, 45, 40)

        # Левый глаз
        pygame.draw.ellipse(self.screen, (255, 255, 255),
                          (cx - 14, eye_y - 5, 12, 10))
        pygame.draw.circle(self.screen, eye_color, (cx - 8, eye_y), 4)
        pygame.draw.circle(self.screen, (30, 25, 20), (cx - 8, eye_y), 2)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx - 7, eye_y - 1), 1)

        # Правый глаз
        pygame.draw.ellipse(self.screen, (255, 255, 255),
                          (cx + 2, eye_y - 5, 12, 10))
        pygame.draw.circle(self.screen, eye_color, (cx + 8, eye_y), 4)
        pygame.draw.circle(self.screen, (30, 25, 20), (cx + 8, eye_y), 2)
        pygame.draw.circle(self.screen, (255, 255, 255), (cx + 9, eye_y - 1), 1)

        # Брови
        brow_color = tuple(max(0, c - 20) for c in hair_col)
        pygame.draw.line(self.screen, brow_color,
                        (cx - 15, eye_y - 9), (cx - 4, eye_y - 8), 2)
        pygame.draw.line(self.screen, brow_color,
                        (cx + 4, eye_y - 8), (cx + 15, eye_y - 9), 2)

        # Нос
        nose_color = tuple(max(0, c - 15) for c in a.skin_color)
        pygame.draw.line(self.screen, nose_color,
                        (cx, eye_y + 3), (cx - 2, eye_y + 10), 2)
        pygame.draw.line(self.screen, nose_color,
                        (cx - 2, eye_y + 10), (cx + 2, eye_y + 12), 2)

        # Рот (если нет бороды или борода маленькая)
        if not a.has_beard:
            mouth_y = head_y + 12
            # Губы
            lip_color = tuple(min(255, c + 20) if i == 0 else c
                             for i, c in enumerate(a.skin_color))
            pygame.draw.arc(self.screen, lip_color,
                           (cx - 8, mouth_y - 2, 16, 10), 3.3, 6.1, 2)

    def _draw_text(self, dialogue_data):
        """Рисуем имя говорящего и текст."""
        text_x = self.avatar_x + self.avatar_size + 25
        name_y = self.box_y + 18

        # Имя
        name_color = dialogue_data.get("portrait_color", COLOR_ACCENT)
        name_surf = self.font_name.render(dialogue_data["speaker"], True, name_color)
        self.screen.blit(name_surf, (text_x, name_y))

        # Декоративная линия под именем
        line_w = min(name_surf.get_width() + 20, self.box_w - self.avatar_size - 80)
        pygame.draw.line(self.screen, (*name_color, 100),
                        (text_x, name_y + 28), (text_x + line_w, name_y + 28), 1)

        # Текст (с печатающим эффектом и переносом)
        displayed_text = dialogue_data["text"][:self.char_index]
        max_line_w = self.box_w - self.avatar_size - 80

        # Разбиваем на строки
        lines = self._wrap_text(displayed_text, max_line_w)

        text_y = name_y + 38
        line_height = self.font_text.get_linesize()

        for i, line in enumerate(lines[:4]):  # Максимум 4 строки
            # Тень текста
            shadow = self.font_text.render(line, True, (0, 0, 0))
            shadow.set_alpha(50)
            self.screen.blit(shadow, (text_x + 1, text_y + 1))

            # Основной текст
            line_surf = self.font_text.render(line, True, COLOR_TEXT)
            self.screen.blit(line_surf, (text_x, text_y))
            text_y += line_height

    def _wrap_text(self, text, max_width):
        """Разбивает текст на строки."""
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if self.font_text.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else [""]

    def _draw_indicators(self):
        """Рисуем индикаторы прогресса и подсказки."""
        # Прогресс диалога
        progress_text = f"{self.current_index + 1}/{len(self.dialogues)}"
        progress_surf = self.font_hint.render(progress_text, True, COLOR_TEXT_DIM)
        self.screen.blit(progress_surf, (self.box_x + 15, self.box_y + self.box_h - 22))

        # Подсказка продолжения
        if self.finished_typing:
            if self.current_index < len(self.dialogues) - 1:
                hint = "SPACE / E — Продолжить"
            else:
                hint = "SPACE / E — Закрыть"

            hint_surf = self.font_hint.render(hint, True, COLOR_TEXT_DIM)
            hint_x = self.box_x + self.box_w - hint_surf.get_width() - 20
            hint_y = self.box_y + self.box_h - 25

            # Мигающий фон
            alpha = int(150 + 80 * math.sin(self.time * 3))
            hint_bg = pygame.Surface((hint_surf.get_width() + 16, 22), pygame.SRCALPHA)
            pygame.draw.rect(hint_bg, (*COLOR_PRIMARY_DARK, alpha // 3),
                           hint_bg.get_rect(), border_radius=5)
            self.screen.blit(hint_bg, (hint_x - 8, hint_y - 3))
            self.screen.blit(hint_surf, (hint_x, hint_y))

            # Мигающий треугольник
            tri_x = self.box_x + self.box_w - 30
            tri_y = self.box_y + self.box_h - 40
            tri_alpha = int(180 + 75 * math.sin(self.time * 4))
            tri_surf = pygame.Surface((14, 12), pygame.SRCALPHA)
            pygame.draw.polygon(tri_surf, (*COLOR_ACCENT[:3], tri_alpha),
                              [(0, 0), (14, 0), (7, 12)])
            self.screen.blit(tri_surf, (tri_x, tri_y))