import pygame
import math
from game.constants import *


class DialogueBox:
    """Диалоговое окно в стиле Genshin Impact."""

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

        self._create_fonts()
        self._calculate_layout()

    def _create_fonts(self):
        self.font_name = pygame.font.SysFont("georgia", 28, bold=True)
        self.font_role = pygame.font.SysFont("segoeui", 16)
        self.font_text = pygame.font.SysFont("segoeui", 20)
        self.font_hint = pygame.font.SysFont("segoeui", 13)

    def _calculate_layout(self):
        sw, sh = self.screen.get_size()

        # Нижняя панель с текстом
        self.box_w = min(900, sw - 80)
        self.box_h = 160
        self.box_x = sw // 2 - self.box_w // 2
        self.box_y = sh - self.box_h - 35
        self.box_rect = pygame.Rect(self.box_x, self.box_y,
                                     self.box_w, self.box_h)

        # Имя персонажа — сверху по центру панели
        self.name_y = self.box_y - 70

        # Текстовая область внутри панели
        self.text_padding_x = 50
        self.text_padding_top = 25
        self.text_max_w = self.box_w - self.text_padding_x * 2

    def start_dialogue(self, dialogues):
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
            while (self.char_timer >= self.char_speed and
                   self.char_index < len(full_text)):
                self.char_timer -= self.char_speed
                self.char_index += 1
        else:
            self.finished_typing = True

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                return self._advance()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._advance()
        return False

    def _advance(self):
        if self.finished_typing:
            self.current_index += 1
            if self.current_index >= len(self.dialogues):
                self.active = False
                return True
            self.char_index = 0
            self.char_timer = 0.0
            self.finished_typing = False
        else:
            self.char_index = len(
                self.dialogues[self.current_index]["text"])
            self.finished_typing = True
        return True

    # ── Отрисовка ────────────────────────────────────────────────────

    def draw(self):
        if not self.active or not self.dialogues:
            return

        current = self.dialogues[self.current_index]
        sw, sh = self.screen.get_size()

        # Затемнение верхней и нижней части экрана (кинематографично)
        self._draw_cinematic_bars(sw, sh)

        # Имя и должность — сверху по центру
        self._draw_name_plate(current, sw)

        # Нижняя панель с текстом
        self._draw_text_box(current, sw)

        # Индикатор продолжения
        self._draw_continue_indicator(sw)

    def _draw_cinematic_bars(self, sw, sh):
        """Кинематографические чёрные полосы сверху и снизу."""
        bar_h = 60
        # Верхняя полоса
        top_bar = pygame.Surface((sw, bar_h), pygame.SRCALPHA)
        for y in range(bar_h):
            alpha = int(200 * (1 - y / bar_h))
            pygame.draw.line(top_bar, (0, 0, 0, alpha),
                             (0, y), (sw, y))
        self.screen.blit(top_bar, (0, 0))

        # Нижняя полоса
        bottom_bar = pygame.Surface((sw, bar_h + 40), pygame.SRCALPHA)
        for y in range(bar_h + 40):
            alpha = int(200 * (y / (bar_h + 40)))
            pygame.draw.line(bottom_bar, (0, 0, 0, alpha),
                             (0, y), (sw, y))
        self.screen.blit(bottom_bar, (0, sh - bar_h - 40))

    def _draw_name_plate(self, dialogue_data, sw):
        """Имя персонажа и должность — по центру над текстовой панелью."""
        speaker = dialogue_data.get("speaker", "???")
        role = dialogue_data.get("role", "")
        portrait_color = dialogue_data.get("portrait_color", (255, 255, 255))

        cx = sw // 2

        # ── Имя ──────────────────────────────────────────────────────

        name_surf = self.font_name.render(speaker, True, (255, 255, 255))
        name_w = name_surf.get_width()
        name_x = cx - name_w // 2
        name_y = self.name_y - 10

        # Фоновая подложка под имя
        plate_w = name_w + 60
        plate_h = 50 if role else 40
        plate_x = cx - plate_w // 2
        plate_y = name_y - 5

        plate = pygame.Surface((plate_w, plate_h), pygame.SRCALPHA)

        # Градиентный фон
        '''for row in range(plate_h):
            ratio = row / plate_h
            alpha = int(180 * (0.5 + 0.5 * math.sin(ratio * math.pi)))
            pygame.draw.line(plate, (0, 0, 0, alpha),
                             (0, row), (plate_w, row))'''

        # Декоративные линии по бокам
        line_color = (*portrait_color[:3], 150)
        line_w = plate_w // 2 - name_w // 2 - 15

        # Левая линия
        for i in range(max(1, line_w)):
            alpha = int(150 * (i / max(1, line_w)))
            pygame.draw.line(plate, (*portrait_color[:3], alpha),
                             (5 + i, plate_h // 2 - (5 if role else 0)),
                             (5 + i, plate_h // 2 - (5 if role else 0)))

        # Правая линия
        for i in range(max(1, line_w)):
            alpha = int(150 * (1 - i / max(1, line_w)))
            rx = plate_w - 5 - line_w + i
            pygame.draw.line(plate, (*portrait_color[:3], alpha),
                             (rx, plate_h // 2 - (5 if role else 0)),
                             (rx, plate_h // 2 - (5 if role else 0)))

        self.screen.blit(plate, (plate_x, plate_y))

        # Имя
        # Тень
        shadow = self.font_name.render(speaker, True, (0, 0, 0))
        shadow.set_alpha(80)
        self.screen.blit(shadow, (name_x + 2, name_y + 2))
        # Основной текст
        self.screen.blit(name_surf, (name_x, name_y))

        # Маленький ромб-разделитель слева и справа от имени
        diamond_y = name_y + name_surf.get_height() // 2
        for dx_offset in [-name_w // 2 - 18, name_w // 2 + 12]:
            diam_x = cx + dx_offset
            points = [
                (diam_x, diamond_y - 5),
                (diam_x + 5, diamond_y),
                (diam_x, diamond_y + 5),
                (diam_x - 5, diamond_y),
            ]
            pygame.draw.polygon(self.screen, portrait_color, points)

        # ── Должность / роль ─────────────────────────────────────────

        if role:
            role_surf = self.font_role.render(role, True, portrait_color)
            role_x = cx - role_surf.get_width() // 2
            role_y = name_y + 45
            self.screen.blit(role_surf, (role_x, role_y))

    def _draw_text_box(self, dialogue_data, sw):
        """Нижняя панель с текстом — justify по ширине."""
        # Фон панели
        box = pygame.Surface((self.box_w, self.box_h), pygame.SRCALPHA)

        # Градиент снизу вверх
        for row in range(self.box_h):
            ratio = row / self.box_h
            # Более прозрачный сверху, плотный снизу
            alpha = int(60 + 160 * ratio)
            r = int(5 + ratio * 8)
            g = int(5 + ratio * 6)
            b = int(10 + ratio * 12)
            pygame.draw.line(box, (r, g, b, alpha),
                             (0, row), (self.box_w, row))

        # Тонкая верхняя линия
        portrait_color = dialogue_data.get("portrait_color", (200, 200, 200))
        for px in range(self.box_w):
            dist = abs(px - self.box_w // 2) / (self.box_w // 2)
            alpha = int(100 * (1 - dist))
            pygame.draw.line(box, (*portrait_color[:3], alpha),
                             (px, 0), (px, 1))

        self.screen.blit(box, (self.box_x, self.box_y))

        # ── Текст (justify) ──────────────────────────────────────────

        displayed = dialogue_data["text"][:self.char_index]
        lines = self._wrap_text(displayed, self.text_max_w)

        text_x = self.box_x + self.text_padding_x
        text_y = self.box_y + self.text_padding_top

        line_height = self.font_text.get_linesize() + 4

        # Полный текст для определения общего кол-ва строк
        full_lines = self._wrap_text(dialogue_data["text"], self.text_max_w)
        max_visible_lines = min(len(full_lines), 4)

        for i, line in enumerate(lines[:max_visible_lines]):
            is_last_line = (i == len(lines) - 1)
            is_full_paragraph_last = (i == len(full_lines) - 1)

            # Justify — растягиваем все строки кроме последней параграфа
            if not is_last_line and not is_full_paragraph_last:
                self._draw_justified_line(line, text_x, text_y,
                                           self.text_max_w)
            else:
                # Последняя строка — обычное выравнивание по левому краю
                # Тень
                shadow = self.font_text.render(line, True, (0, 0, 0))
                shadow.set_alpha(60)
                self.screen.blit(shadow, (text_x + 1, text_y + 1))
                # Текст
                surf = self.font_text.render(line, True, (255, 255, 255))
                self.screen.blit(surf, (text_x, text_y))

            text_y += line_height

        # Номер реплики
        progress = f"{self.current_index + 1}/{len(self.dialogues)}"
        prog_surf = self.font_hint.render(progress, True, (120, 120, 130))
        self.screen.blit(prog_surf,
                         (self.box_x + self.box_w - prog_surf.get_width() - 20,
                          self.box_y + self.box_h - 22))

    def _draw_justified_line(self, line, x, y, max_width):
        """Рисует строку с выравниванием по ширине (justify)."""
        words = line.split()
        if len(words) <= 1:
            shadow = self.font_text.render(line, True, (0, 0, 0))
            shadow.set_alpha(60)
            self.screen.blit(shadow, (x + 1, y + 1))
            surf = self.font_text.render(line, True, (255, 255, 255))
            self.screen.blit(surf, (x, y))
            return

        # Считаем ширину всех слов
        word_surfaces = []
        total_words_w = 0
        for word in words:
            ws = self.font_text.render(word, True, (255, 255, 255))
            word_surfaces.append(ws)
            total_words_w += ws.get_width()

        # Равномерный пробел между словами
        total_space = max_width - total_words_w
        space_between = total_space / max(1, len(words) - 1)

        # Рисуем
        current_x = float(x)
        for i, ws in enumerate(word_surfaces):
            # Тень
            shadow = self.font_text.render(words[i], True, (0, 0, 0))
            shadow.set_alpha(60)
            self.screen.blit(shadow, (int(current_x) + 1, y + 1))
            # Слово
            self.screen.blit(ws, (int(current_x), y))
            current_x += ws.get_width() + space_between

    def _draw_continue_indicator(self, sw):
        """Мигающий индикатор продолжения."""
        if not self.finished_typing:
            return

        # Мигающий треугольник внизу
        pulse = math.sin(self.time * 4) * 0.5 + 0.5
        alpha = int(120 + 135 * pulse)

        tri_x = sw // 2
        tri_y = self.box_y + self.box_h + 10 + int(pulse * 5)

        tri_surf = pygame.Surface((20, 14), pygame.SRCALPHA)
        pygame.draw.polygon(tri_surf, (255, 255, 255, alpha),
                            [(0, 0), (20, 0), (10, 14)])
        self.screen.blit(tri_surf, (tri_x - 10, tri_y))

        # Подсказка
        if self.current_index < len(self.dialogues) - 1:
            hint = "Нажмите, чтобы продолжить"
        else:
            hint = "Нажмите, чтобы закрыть"

        hint_surf = self.font_hint.render(hint, True, (150, 150, 160))
        hint_surf.set_alpha(alpha)
        self.screen.blit(hint_surf,
                         (sw // 2 - hint_surf.get_width() // 2,
                          tri_y + 18))

    # ── Вспомогательные ──────────────────────────────────────────────

    def _wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if self.font_text.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines if lines else [""]