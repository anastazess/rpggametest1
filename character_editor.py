"""
Редактор персонажей — Echoes of the Fallen
Визуально настраивай внешность NPC и получай готовый код.

Запуск: python character_editor.py
"""

import pygame
import math
import sys
import os
import pyperclip  # pip install pyperclip (опционально)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.world.npc import NPC, NPCAppearance


# ══════════════════════════════════════════════════════════════════════
# Константы редактора
# ══════════════════════════════════════════════════════════════════════

SCREEN_W, SCREEN_H = 1400, 780

HAIR_STYLES = ["short", "long", "ponytail", "bald"]
ACCESSORIES = ["", "apron", "hood", "cape"]
ACCESSORY_NAMES = {"": "Нет", "apron": "Фартук", "hood": "Капюшон", "cape": "Плащ"}
HAIR_STYLE_NAMES = {"short": "Короткие", "long": "Длинные",
                     "ponytail": "Хвост", "bald": "Лысый"}
ROLES = ["villager", "guard", "merchant", "blacksmith", "innkeeper",
         "priestess", "sage", "barmaid", "hunter", "child", "noble"]

PRESET_COLORS = {
    "skin": [
        (255, 224, 196), (240, 200, 170), (220, 185, 155),
        (200, 165, 135), (180, 140, 110), (150, 110, 85),
        (120, 85, 65),   (90, 65, 50),
    ],
    "hair": [
        (30, 25, 20),    (60, 40, 25),    (100, 70, 40),
        (140, 100, 60),  (180, 140, 80),  (220, 200, 160),
        (200, 50, 30),   (150, 80, 50),   (80, 60, 100),
        (200, 200, 210),
    ],
    "outfit": [
        (80, 60, 50),    (100, 80, 70),   (70, 90, 70),
        (90, 80, 110),   (120, 90, 80),   (80, 80, 100),
        (110, 100, 80),  (60, 70, 90),    (130, 110, 130),
        (100, 50, 50),
    ],
    "hat": [
        (60, 50, 40),    (80, 70, 55),    (100, 85, 65),
        (70, 60, 80),    (50, 50, 50),    (120, 100, 80),
    ],
}


# ══════════════════════════════════════════════════════════════════════
# UI элементы
# ══════════════════════════════════════════════════════════════════════

class ColorPicker:
    """Выбор цвета из палитры + ручной RGB."""

    def __init__(self, x, y, label, presets, initial_color):
        self.x = x
        self.y = y
        self.label = label
        self.presets = presets
        self.color = list(initial_color)
        self.expanded = False
        self.dragging_channel = -1  # 0=R, 1=G, 2=B

        self.font_label = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 12)
        self.font_tiny  = pygame.font.SysFont("segoeui", 10)

    def get_height(self):
        if self.expanded:
            rows = (len(self.presets) + 7) // 8
            return 30 + rows * 28 + 90
        return 30

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Заголовок — раскрыть/свернуть
            header = pygame.Rect(self.x, self.y, 250, 25)
            if header.collidepoint(mx, my):
                self.expanded = not self.expanded
                return True

            if not self.expanded:
                return False

            # Палитра
            preset_y = self.y + 30
            for i, c in enumerate(self.presets):
                col = i % 8
                row = i // 8
                px = self.x + col * 30
                py = preset_y + row * 28
                r = pygame.Rect(px, py, 26, 24)
                if r.collidepoint(mx, my):
                    self.color = list(c)
                    return True

            # RGB слайдеры
            rows = (len(self.presets) + 7) // 8
            slider_y = preset_y + rows * 28 + 10
            for ch in range(3):
                sy = slider_y + ch * 25
                sr = pygame.Rect(self.x + 25, sy, 200, 16)
                if sr.collidepoint(mx, my):
                    self.dragging_channel = ch
                    rel = mx - sr.x
                    self.color[ch] = max(0, min(255, int(rel / 200 * 255)))
                    return True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging_channel = -1

        if event.type == pygame.MOUSEMOTION and self.dragging_channel >= 0:
            mx = event.pos[0]
            sr_x = self.x + 25
            rel = mx - sr_x
            self.color[self.dragging_channel] = max(0, min(255, int(rel / 200 * 255)))
            return True

        return False

    def draw(self, surface):
        # Заголовок
        arrow = "▼" if self.expanded else "▶"
        label_text = f"{arrow} {self.label}"
        ls = self.font_label.render(label_text, True, COLOR_TEXT)
        surface.blit(ls, (self.x, self.y + 2))

        # Цветной квадратик рядом с заголовком
        pygame.draw.rect(surface, tuple(self.color),
                         (self.x + 220, self.y + 2, 24, 20), border_radius=4)
        pygame.draw.rect(surface, (100, 90, 110),
                         (self.x + 220, self.y + 2, 24, 20), width=1, border_radius=4)

        if not self.expanded:
            return

        # Палитра
        preset_y = self.y + 30
        for i, c in enumerate(self.presets):
            col = i % 8
            row = i // 8
            px = self.x + col * 30
            py = preset_y + row * 28

            pygame.draw.rect(surface, c, (px, py, 26, 24), border_radius=4)

            is_selected = (abs(c[0] - self.color[0]) < 3 and
                           abs(c[1] - self.color[1]) < 3 and
                           abs(c[2] - self.color[2]) < 3)
            if is_selected:
                pygame.draw.rect(surface, COLOR_ACCENT,
                                 (px - 2, py - 2, 30, 28), width=2, border_radius=5)
            else:
                pygame.draw.rect(surface, (80, 70, 90),
                                 (px, py, 26, 24), width=1, border_radius=4)

        # RGB слайдеры
        rows = (len(self.presets) + 7) // 8
        slider_y = preset_y + rows * 28 + 10

        channel_names = ["R", "G", "B"]
        channel_colors = [(200, 60, 60), (60, 200, 60), (60, 60, 200)]

        for ch in range(3):
            sy = slider_y + ch * 25
            val = self.color[ch]

            # Метка
            n = self.font_small.render(channel_names[ch], True, channel_colors[ch])
            surface.blit(n, (self.x, sy))

            # Трек
            pygame.draw.rect(surface, (40, 35, 55),
                             (self.x + 25, sy, 200, 16), border_radius=4)

            # Градиент
            for px in range(200):
                ratio = px / 200
                c = [self.color[0], self.color[1], self.color[2]]
                c[ch] = int(ratio * 255)
                pygame.draw.line(surface, tuple(c),
                                 (self.x + 25 + px, sy + 2),
                                 (self.x + 25 + px, sy + 14))

            # Ручка
            hx = self.x + 25 + int(val / 255 * 200)
            pygame.draw.circle(surface, (255, 255, 255), (hx, sy + 8), 7)
            pygame.draw.circle(surface, channel_colors[ch], (hx, sy + 8), 5)

            # Значение
            vs = self.font_tiny.render(str(val), True, COLOR_TEXT_DIM)
            surface.blit(vs, (self.x + 230, sy + 1))

    def get_color(self):
        return tuple(self.color)


class ToggleButton:
    """Кнопка-переключатель."""

    def __init__(self, x, y, label, options, option_names=None, initial=0):
        self.x = x
        self.y = y
        self.label = label
        self.options = options
        self.option_names = option_names or {o: o for o in options}
        self.index = initial
        self.font = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_val = pygame.font.SysFont("segoeui", 14)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Стрелка влево
            left_rect = pygame.Rect(self.x + 120, self.y, 25, 22)
            if left_rect.collidepoint(event.pos):
                self.index = (self.index - 1) % len(self.options)
                return True
            # Стрелка вправо
            right_rect = pygame.Rect(self.x + 235, self.y, 25, 22)
            if right_rect.collidepoint(event.pos):
                self.index = (self.index + 1) % len(self.options)
                return True
        return False

    def draw(self, surface):
        ls = self.font.render(self.label + ":", True, COLOR_TEXT)
        surface.blit(ls, (self.x, self.y + 2))

        # Стрелки
        for arrow, ax in [("◀", self.x + 120), ("▶", self.x + 235)]:
            bg = pygame.Surface((25, 22), pygame.SRCALPHA)
            pygame.draw.rect(bg, (50, 45, 65, 200), bg.get_rect(), border_radius=4)
            surface.blit(bg, (ax, self.y))
            a = self.font_val.render(arrow, True, COLOR_TEXT)
            surface.blit(a, (ax + 6, self.y + 1))

        # Значение
        val = self.option_names.get(self.options[self.index], str(self.options[self.index]))
        vs = self.font_val.render(val, True, COLOR_ACCENT)
        vx = self.x + 148 + (85 - vs.get_width()) // 2
        surface.blit(vs, (vx, self.y + 2))

    def get_value(self):
        return self.options[self.index]


class CheckBox:
    """Чекбокс."""

    def __init__(self, x, y, label, initial=False):
        self.x = x
        self.y = y
        self.label = label
        self.checked = initial
        self.font = pygame.font.SysFont("segoeui", 14, bold=True)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            r = pygame.Rect(self.x, self.y, 200, 22)
            if r.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False

    def draw(self, surface):
        # Коробка
        box = pygame.Rect(self.x, self.y + 2, 18, 18)
        pygame.draw.rect(surface, (50, 45, 65), box, border_radius=3)
        pygame.draw.rect(surface, COLOR_PRIMARY_DARK, box, width=1, border_radius=3)

        if self.checked:
            pygame.draw.line(surface, COLOR_ACCENT,
                             (self.x + 3, self.y + 11), (self.x + 7, self.y + 16), 3)
            pygame.draw.line(surface, COLOR_ACCENT,
                             (self.x + 7, self.y + 16), (self.x + 15, self.y + 5), 3)

        ls = self.font.render(self.label, True, COLOR_TEXT)
        surface.blit(ls, (self.x + 25, self.y + 1))


class TextInput:
    """Поле ввода текста."""

    def __init__(self, x, y, w, label, initial=""):
        self.x = x
        self.y = y
        self.w = w
        self.label = label
        self.text = initial
        self.active = False
        self.cursor_blink = 0.0
        self.font_label = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_input = pygame.font.SysFont("segoeui", 14)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            r = pygame.Rect(self.x, self.y + 20, self.w, 26)
            self.active = r.collidepoint(event.pos)
            return self.active

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif event.unicode and len(self.text) < 40:
                self.text += event.unicode
            return True
        return False

    def draw(self, surface, dt=0):
        self.cursor_blink += dt

        ls = self.font_label.render(self.label + ":", True, COLOR_TEXT)
        surface.blit(ls, (self.x, self.y))

        # Поле
        box = pygame.Rect(self.x, self.y + 20, self.w, 26)
        border = COLOR_ACCENT if self.active else COLOR_PRIMARY_DARK
        pygame.draw.rect(surface, (35, 30, 50), box, border_radius=5)
        pygame.draw.rect(surface, border, box, width=1, border_radius=5)

        ts = self.font_input.render(self.text, True, COLOR_TEXT)
        surface.blit(ts, (self.x + 6, self.y + 24))

        # Курсор
        if self.active and int(self.cursor_blink * 2) % 2 == 0:
            cx = self.x + 6 + ts.get_width() + 2
            pygame.draw.line(surface, COLOR_ACCENT, (cx, self.y + 24), (cx, self.y + 42), 2)


# ══════════════════════════════════════════════════════════════════════
# Рендер персонажа (из dialogue.py)
# ══════════════════════════════════════════════════════════════════════

def render_npc_preview(surface, cx, cy, size, appearance):
    """Рисуем большой портрет персонажа."""
    a = appearance

    # Тело
    body_w = int(size * 0.55)
    body_h = int(size * 0.45)
    pygame.draw.ellipse(surface, tuple(max(0, c - 20) for c in a.outfit_color),
                        (cx - body_w // 2 + 3, cy + 13, body_w, body_h))
    pygame.draw.ellipse(surface, a.outfit_color,
                        (cx - body_w // 2, cy + 10, body_w, body_h))

    collar = tuple(min(255, c + 25) for c in a.outfit_color)
    pygame.draw.arc(surface, collar, (cx - 15, cy + 5, 30, 20), 0, math.pi, 3)

    if a.accessory == "apron":
        pygame.draw.rect(surface, (235, 225, 210),
                         (cx - 18, cy + 18, 36, 30), border_radius=3)
    if a.accessory == "hood":
        hood = tuple(max(0, c - 15) for c in a.outfit_color)
        pygame.draw.ellipse(surface, hood, (cx - 28, cy - 30, 56, 45))
        pygame.draw.ellipse(surface, a.outfit_color, (cx - 24, cy - 25, 48, 38))
    if a.accessory == "cape":
        cape = tuple(max(0, c - 20) for c in a.outfit_color)
        pygame.draw.polygon(surface, cape,
                            [(cx - 30, cy + 5), (cx + 30, cy + 5),
                             (cx + 35, cy + 50), (cx - 35, cy + 50)])

    # Голова
    hr = int(size * 0.26)
    hy = cy - 12
    pygame.draw.circle(surface, tuple(max(0, c - 20) for c in a.skin_color),
                       (cx + 2, hy + 2), hr)
    pygame.draw.circle(surface, a.skin_color, (cx, hy), hr)

    blush = tuple(min(255, c + 20) if i == 0 else max(0, c - 10)
                  for i, c in enumerate(a.skin_color))
    pygame.draw.circle(surface, blush, (cx - 16, hy + 8), 6)
    pygame.draw.circle(surface, blush, (cx + 16, hy + 8), 6)

    # Волосы
    hc = a.hair_color
    if a.hair_style == "short":
        pygame.draw.arc(surface, hc, (cx - hr - 2, hy - hr - 5, hr * 2 + 4, hr + 10),
                        0, math.pi, 8)
        pygame.draw.ellipse(surface, hc, (cx - 18, hy - hr + 2, 36, 18))
    elif a.hair_style == "long":
        pygame.draw.arc(surface, hc, (cx - hr - 2, hy - hr - 5, hr * 2 + 4, hr + 10),
                        0, math.pi, 8)
        pygame.draw.ellipse(surface, hc, (cx - hr - 8, hy - 10, 16, 50))
        pygame.draw.ellipse(surface, hc, (cx + hr - 8, hy - 10, 16, 50))
        pygame.draw.ellipse(surface, hc, (cx - 18, hy - hr + 2, 36, 18))
    elif a.hair_style == "ponytail":
        pygame.draw.arc(surface, hc, (cx - hr - 2, hy - hr - 5, hr * 2 + 4, hr + 10),
                        0, math.pi, 8)
        pygame.draw.ellipse(surface, hc, (cx - 6, hy - hr - 15, 12, 20))
        pygame.draw.ellipse(surface, tuple(max(0, c - 30) for c in hc),
                            (cx - 4, hy - hr - 2, 8, 6))
        pygame.draw.ellipse(surface, hc, (cx - 15, hy - hr + 3, 30, 14))
    elif a.hair_style == "bald":
        pygame.draw.ellipse(surface, tuple(min(255, c + 30) for c in a.skin_color),
                            (cx - 8, hy - hr + 5, 16, 10))

    # Борода
    if a.has_beard:
        pygame.draw.ellipse(surface, hc, (cx - 14, hy + 8, 28, 25))
        pygame.draw.ellipse(surface, hc, (cx - 10, hy + 15, 20, 18))

    # Шляпа
    if a.has_hat:
        hat_y = hy - hr - 3
        pygame.draw.ellipse(surface, a.hat_color, (cx - 28, hat_y, 56, 14))
        pygame.draw.rect(surface, a.hat_color, (cx - 16, hat_y - 18, 32, 22), border_radius=5)
        pygame.draw.rect(surface, tuple(max(0, c - 30) for c in a.hat_color),
                         (cx - 16, hat_y - 5, 32, 5))

    # Глаза
    ey = hy - 2
    pygame.draw.ellipse(surface, (255, 255, 255), (cx - 14, ey - 5, 12, 10))
    pygame.draw.circle(surface, (55, 45, 40), (cx - 8, ey), 4)
    pygame.draw.circle(surface, (30, 25, 20), (cx - 8, ey), 2)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 7, ey - 1), 1)

    pygame.draw.ellipse(surface, (255, 255, 255), (cx + 2, ey - 5, 12, 10))
    pygame.draw.circle(surface, (55, 45, 40), (cx + 8, ey), 4)
    pygame.draw.circle(surface, (30, 25, 20), (cx + 8, ey), 2)
    pygame.draw.circle(surface, (255, 255, 255), (cx + 9, ey - 1), 1)

    # Брови
    bc = tuple(max(0, c - 20) for c in hc)
    pygame.draw.line(surface, bc, (cx - 15, ey - 9), (cx - 4, ey - 8), 2)
    pygame.draw.line(surface, bc, (cx + 4, ey - 8), (cx + 15, ey - 9), 2)

    # Нос
    nc = tuple(max(0, c - 15) for c in a.skin_color)
    pygame.draw.line(surface, nc, (cx, ey + 3), (cx - 2, ey + 10), 2)

    # Рот
    if not a.has_beard:
        lip = tuple(min(255, c + 20) if i == 0 else c for i, c in enumerate(a.skin_color))
        pygame.draw.arc(surface, lip, (cx - 8, hy + 10, 16, 10), 3.3, 6.1, 2)


# ══════════════════════════════════════════════════════════════════════
# Генерация кода
# ══════════════════════════════════════════════════════════════════════

def generate_code(name, role, appearance, dialogues_text):
    """Генерирует Python-код для NPC."""
    a = appearance
    lines = []
    lines.append(f'def create_{role.lower().replace(" ", "_")}() -> NPC:')
    lines.append(f'    """Созданный в редакторе: {name}."""')
    lines.append(f'    appearance = NPCAppearance(')
    lines.append(f'        body_color   = {a.body_color},')
    lines.append(f'        skin_color   = {a.skin_color},')
    lines.append(f'        hair_color   = {a.hair_color},')
    lines.append(f'        hair_style   = "{a.hair_style}",')
    lines.append(f'        outfit_color = {a.outfit_color},')
    lines.append(f'        has_beard    = {a.has_beard},')
    lines.append(f'        has_hat      = {a.has_hat},')
    if a.has_hat:
        lines.append(f'        hat_color    = {a.hat_color},')
    lines.append(f'        accessory    = "{a.accessory}",')
    lines.append(f'    )')
    lines.append(f'    dialogues = [')

    for d in dialogues_text.split("\\n"):
        d = d.strip()
        if d:
            lines.append(f'        {{"speaker": "{name}",')
            lines.append(f'         "text": "{d}",')
            lines.append(f'         "portrait_color": {a.body_color}}},')

    lines.append(f'    ]')
    lines.append(f'    npc = NPC(0, 0, "{name}",')
    lines.append(f'              appearance, dialogues, "{role}")')
    lines.append(f'    return npc')

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
# Главное окно
# ══════════════════════════════════════════════════════════════════════

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Редактор персонажей — Echoes of the Fallen")
    clock = pygame.time.Clock()

    # Шрифты
    font_title   = pygame.font.SysFont("georgia", 26, bold=True)
    font_heading = pygame.font.SysFont("segoeui", 16, bold=True)
    font_normal  = pygame.font.SysFont("segoeui", 14)
    font_small   = pygame.font.SysFont("segoeui", 12)
    font_code    = pygame.font.SysFont("consolas", 12)
    font_btn     = pygame.font.SysFont("segoeui", 14, bold=True)

    # ── UI элементы ──────────────────────────────────────────────────

    PANEL_X = 20
    PANEL_Y = 70

    name_input = TextInput(PANEL_X, PANEL_Y, 260, "Имя персонажа", "Новый NPC")
    dialogue_input = TextInput(PANEL_X, PANEL_Y + 55, 260, "Реплика",
                                "Приветствую, путник!")

    role_toggle = ToggleButton(PANEL_X, PANEL_Y + 115, "Роль", ROLES)
    hair_toggle = ToggleButton(PANEL_X, PANEL_Y + 145, "Причёска", HAIR_STYLES,
                                HAIR_STYLE_NAMES)
    accessory_toggle = ToggleButton(PANEL_X, PANEL_Y + 175, "Аксессуар", ACCESSORIES,
                                     ACCESSORY_NAMES)

    beard_check = CheckBox(PANEL_X, PANEL_Y + 210, "Борода")
    hat_check   = CheckBox(PANEL_X + 130, PANEL_Y + 210, "Шляпа")

    # Цвета
    color_y = PANEL_Y + 250
    skin_picker   = ColorPicker(PANEL_X, color_y, "Кожа",
                                 PRESET_COLORS["skin"], (225, 190, 165))
    outfit_picker = ColorPicker(PANEL_X, 0, "Одежда",
                                 PRESET_COLORS["outfit"], (100, 80, 70))
    hair_picker   = ColorPicker(PANEL_X, 0, "Волосы",
                                 PRESET_COLORS["hair"], (60, 40, 25))
    hat_picker    = ColorPicker(PANEL_X, 0, "Шляпа",
                                 PRESET_COLORS["hat"], (80, 70, 55))

    pickers = [skin_picker, outfit_picker, hair_picker, hat_picker]

    # Код
    generated_code = ""
    code_scroll = 0
    show_copied = 0.0

    # Фон
    bg = pygame.Surface((SCREEN_W, SCREEN_H))
    for y in range(SCREEN_H):
        ratio = y / SCREEN_H
        r = int(12 + ratio * 8)
        g = int(10 + ratio * 6)
        b = int(24 + ratio * 14)
        pygame.draw.line(bg, (r, g, b), (0, y), (SCREEN_W, y))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if show_copied > 0:
            show_copied -= dt

        # ── Пересчёт Y для пикеров ──────────────────────────────────
        current_y = color_y
        for picker in pickers:
            picker.y = current_y
            current_y += picker.get_height() + 8

        # ── Собираем Appearance ──────────────────────────────────────
        appearance = NPCAppearance(
            body_color   = outfit_picker.get_color(),
            skin_color   = skin_picker.get_color(),
            hair_color   = hair_picker.get_color(),
            hair_style   = hair_toggle.get_value(),
            outfit_color = outfit_picker.get_color(),
            has_beard    = beard_check.checked,
            has_hat      = hat_check.checked,
            hat_color    = hat_picker.get_color(),
            accessory    = accessory_toggle.get_value(),
        )

        # ── События ──────────────────────────────────────────────────

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            name_input.handle_event(event)
            dialogue_input.handle_event(event)
            role_toggle.handle_event(event)
            hair_toggle.handle_event(event)
            accessory_toggle.handle_event(event)
            beard_check.handle_event(event)
            hat_check.handle_event(event)

            for picker in pickers:
                picker.handle_event(event)

            # Кнопка «Генерировать»
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                gen_btn = pygame.Rect(SCREEN_W - 420, SCREEN_H - 55, 180, 38)
                if gen_btn.collidepoint(event.pos):
                    generated_code = generate_code(
                        name_input.text,
                        role_toggle.get_value(),
                        appearance,
                        dialogue_input.text,
                    )
                    code_scroll = 0

                copy_btn = pygame.Rect(SCREEN_W - 220, SCREEN_H - 55, 180, 38)
                if copy_btn.collidepoint(event.pos) and generated_code:
                    try:
                        pyperclip.copy(generated_code)
                        show_copied = 2.0
                    except Exception:
                        show_copied = -2.0  # ошибка

            # Прокрутка кода
            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                code_panel = pygame.Rect(SCREEN_W - 450, 70, 430, SCREEN_H - 140)
                if code_panel.collidepoint(mx, my):
                    code_scroll = max(0, code_scroll - event.y * 3)

        # ── Отрисовка ────────────────────────────────────────────────

        screen.blit(bg, (0, 0))

        # Заголовок
        ts = font_title.render("Редактор персонажей", True, COLOR_PRIMARY_LIGHT)
        screen.blit(ts, (20, 20))

        # ── Левая панель: параметры ──────────────────────────────────

        panel_bg = pygame.Surface((300, SCREEN_H - 60), pygame.SRCALPHA)
        pygame.draw.rect(panel_bg, (18, 15, 28, 180),
                         panel_bg.get_rect(), border_radius=10)
        screen.blit(panel_bg, (10, 60))

        name_input.draw(screen, dt)
        dialogue_input.draw(screen, dt)
        role_toggle.draw(screen)
        hair_toggle.draw(screen)
        accessory_toggle.draw(screen)
        beard_check.draw(screen)
        hat_check.draw(screen)

        for picker in pickers:
            picker.draw(screen)

        # ── Центральная панель: превью ───────────────────────────────

        preview_cx = 500
        preview_cy = SCREEN_H // 2
        preview_r  = 140

        # Пьедестал
        ped = pygame.Surface((preview_r * 2 + 30, preview_r * 2 + 30), pygame.SRCALPHA)
        pygame.draw.circle(ped, (28, 24, 42, 180),
                           (preview_r + 15, preview_r + 15), preview_r)
        pygame.draw.circle(ped, (*COLOR_PRIMARY_DARK, 130),
                           (preview_r + 15, preview_r + 15), preview_r, width=2)
        screen.blit(ped, (preview_cx - preview_r - 15, preview_cy - preview_r - 15))

        render_npc_preview(screen, preview_cx, preview_cy, 100, appearance)

        # Имя под превью
        name_s = font_heading.render(name_input.text, True, COLOR_ACCENT)
        screen.blit(name_s, (preview_cx - name_s.get_width() // 2, preview_cy + preview_r + 20))

        role_s = font_small.render(role_toggle.get_value(), True, COLOR_TEXT_DIM)
        screen.blit(role_s, (preview_cx - role_s.get_width() // 2, preview_cy + preview_r + 42))

        # Мини-превью спрайта
        mini_npc = NPC(0, 0, name_input.text, appearance, [], role_toggle.get_value())
        directions = ["down", "left", "right", "up"]
        mini_start_x = preview_cx - 120
        mini_y = preview_cy + preview_r + 70

        for i, d in enumerate(directions):
            ms = pygame.Surface((50, 60), pygame.SRCALPHA)
            mini_npc.x = 9
            mini_npc.y = 6
            mini_npc.direction = d
            mini_npc.moving = False
            mini_npc.hovered = False
            mini_npc.anim_time = pygame.time.get_ticks() / 1000
            mini_npc.draw(ms, 0, 0)

            frame = pygame.Surface((54, 64), pygame.SRCALPHA)
            pygame.draw.rect(frame, (28, 24, 42, 180), frame.get_rect(), border_radius=5)
            screen.blit(frame, (mini_start_x + i * 62 - 2, mini_y - 2))
            screen.blit(ms, (mini_start_x + i * 62, mini_y))

            dl = font_small.render(d, True, COLOR_TEXT_DIM)
            screen.blit(dl, (mini_start_x + i * 62 + 25 - dl.get_width() // 2, mini_y + 64))

        # ── Правая панель: код ───────────────────────────────────────

        code_x = SCREEN_W - 450
        code_y = 70
        code_w = 430
        code_h = SCREEN_H - 140

        code_bg = pygame.Surface((code_w, code_h), pygame.SRCALPHA)
        pygame.draw.rect(code_bg, (15, 12, 25, 220),
                         code_bg.get_rect(), border_radius=10)
        pygame.draw.rect(code_bg, (*COLOR_PRIMARY_DARK, 130),
                         code_bg.get_rect(), width=1, border_radius=10)
        screen.blit(code_bg, (code_x, code_y))

        code_title = font_heading.render("Сгенерированный код", True, COLOR_PRIMARY_LIGHT)
        screen.blit(code_title, (code_x + 14, code_y + 10))

        if generated_code:
            code_lines = generated_code.split("\n")
            clip_rect = pygame.Rect(code_x + 8, code_y + 35, code_w - 16, code_h - 45)
            old_clip = screen.get_clip()
            screen.set_clip(clip_rect)

            for i, line in enumerate(code_lines):
                ly = code_y + 38 + (i - code_scroll) * 16
                if ly < code_y + 30 or ly > code_y + code_h:
                    continue

                # Подсветка синтаксиса
                color = (180, 180, 190)
                stripped = line.strip()
                if stripped.startswith("def "):
                    color = (120, 180, 255)
                elif stripped.startswith('"""') or stripped.startswith('#'):
                    color = (100, 160, 100)
                elif stripped.startswith('"') or "'" in stripped:
                    color = (200, 170, 120)
                elif any(kw in stripped for kw in ["True", "False", "None"]):
                    color = (200, 120, 180)
                elif stripped.startswith("return"):
                    color = (200, 120, 120)

                ls = font_code.render(line, True, color)
                screen.blit(ls, (code_x + 14, ly))

            screen.set_clip(old_clip)

            # Номер строки
            total_s = font_small.render(f"{len(code_lines)} строк", True, COLOR_TEXT_DIM)
            screen.blit(total_s, (code_x + code_w - total_s.get_width() - 10,
                                   code_y + code_h - 18))
        else:
            hint = font_normal.render("Нажмите «Генерировать»", True, COLOR_TEXT_DIM)
            screen.blit(hint, (code_x + code_w // 2 - hint.get_width() // 2,
                               code_y + code_h // 2))

        # ── Кнопки ───────────────────────────────────────────────────

        # Генерировать
        gen_rect = pygame.Rect(SCREEN_W - 420, SCREEN_H - 55, 180, 38)
        gen_bg = pygame.Surface((180, 38), pygame.SRCALPHA)
        pygame.draw.rect(gen_bg, (40, 60, 40, 220), gen_bg.get_rect(), border_radius=8)
        pygame.draw.rect(gen_bg, COLOR_SUCCESS, gen_bg.get_rect(), width=2, border_radius=8)
        screen.blit(gen_bg, gen_rect.topleft)
        gs = font_btn.render("Генерировать код", True, COLOR_SUCCESS)
        screen.blit(gs, (gen_rect.centerx - gs.get_width() // 2,
                         gen_rect.centery - gs.get_height() // 2))

        # Копировать
        copy_rect = pygame.Rect(SCREEN_W - 220, SCREEN_H - 55, 180, 38)
        copy_bg = pygame.Surface((180, 38), pygame.SRCALPHA)
        has_code = bool(generated_code)
        cb_color = COLOR_PRIMARY if has_code else COLOR_TEXT_DIM
        pygame.draw.rect(copy_bg, (40, 35, 60, 220), copy_bg.get_rect(), border_radius=8)
        pygame.draw.rect(copy_bg, cb_color, copy_bg.get_rect(), width=2, border_radius=8)
        screen.blit(copy_bg, copy_rect.topleft)
        cs = font_btn.render("Копировать", True, cb_color)
        screen.blit(cs, (copy_rect.centerx - cs.get_width() // 2,
                         copy_rect.centery - cs.get_height() // 2))

        # Уведомление о копировании
        if show_copied > 0:
            msg = font_normal.render("Код скопирован в буфер обмена!", True, COLOR_SUCCESS)
            screen.blit(msg, (SCREEN_W - 420, SCREEN_H - 80))
        elif show_copied < 0:
            msg = font_normal.render("Ошибка: pip install pyperclip", True, COLOR_DANGER)
            screen.blit(msg, (SCREEN_W - 420, SCREEN_H - 80))

        # Подсказка
        footer = font_small.render(
            "ESC — выход  |  Настройте параметры слева → превью в центре → код справа",
            True, COLOR_TEXT_DIM)
        screen.blit(footer, (SCREEN_W // 2 - footer.get_width() // 2, SCREEN_H - 18))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()