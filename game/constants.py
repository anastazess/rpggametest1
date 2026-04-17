# ============================================
# Echoes of the Fallen - Constants
# Studio: sinnerdevdevdev | 2026
# ============================================

import pygame

GAME_TITLE = "Echoes of the Fallen"
STUDIO_NAME = "sinnerdevdevdev"
STUDIO_YEAR = 2026

# Доступные разрешения
RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
]

# Режимы отображения
DISPLAY_MODES = ["windowed", "fullscreen", "borderless"]
DISPLAY_MODE_NAMES = {
    "windowed": "Оконный",
    "fullscreen": "Полный экран",
    "borderless": "Без рамки",
}

# Цвета
COLOR_BG_DARK = (10, 10, 18)
COLOR_BG_MEDIUM = (20, 20, 35)
COLOR_PRIMARY = (180, 140, 255)
COLOR_PRIMARY_DARK = (120, 80, 200)
COLOR_PRIMARY_LIGHT = (220, 200, 255)
COLOR_ACCENT = (255, 180, 50)
COLOR_ACCENT_GLOW = (255, 200, 100)
COLOR_TEXT = (230, 220, 245)
COLOR_TEXT_DIM = (140, 130, 160)
COLOR_BUTTON_BG = (30, 25, 50)
COLOR_BUTTON_HOVER = (50, 40, 80)
COLOR_BUTTON_BORDER = (100, 70, 180)
COLOR_BUTTON_BORDER_HOVER = (180, 140, 255)
COLOR_SLIDER_BG = (40, 35, 60)
COLOR_SLIDER_FILL = (140, 100, 220)
COLOR_SLIDER_HANDLE = (220, 200, 255)
COLOR_DANGER = (220, 60, 60)
COLOR_SUCCESS = (60, 200, 120)
COLOR_PANEL_BG = (15, 12, 28, 220)
COLOR_OVERLAY = (0, 0, 0, 150)

# Шрифты
FONT_SIZES = {
    "title": 72,
    "subtitle": 28,
    "heading": 36,
    "button": 26,
    "normal": 22,
    "small": 18,
    "tiny": 14,
}

# Названия клавиш для интерфейса
KEYBIND_NAMES = {
    "inventory": "Инвентарь",
    "map": "Карта",
    "journal": "Журнал",
    "interact": "Взаимодействие",
    "pause": "Пауза",
    "attack": "Атака",
    "dodge": "Уворот",
    "use_item": "Использовать предмет",
}

# Клавиши по умолчанию (используем pygame.K_* напрямую)
DEFAULT_KEYBINDINGS = {
    "inventory": pygame.K_i,
    "map": pygame.K_m,
    "journal": pygame.K_j,
    "interact": pygame.K_e,
    "pause": pygame.K_ESCAPE,
    "attack": pygame.K_SPACE,
    "dodge": pygame.K_LSHIFT,
    "use_item": pygame.K_q,
}