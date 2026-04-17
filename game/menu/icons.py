import pygame
import math


class Icons:
    """Программно нарисованные иконки вместо эмодзи."""

    @staticmethod
    def draw_sword(surface, x, y, size=20, color=(220, 200, 255)):
        """Меч — для 'Новая игра'."""
        cx, cy = x + size // 2, y + size // 2
        s = size / 20

        # Лезвие
        pygame.draw.line(surface, color,
                         (int(cx - 7 * s), int(cy + 7 * s)),
                         (int(cx + 7 * s), int(cy - 7 * s)), max(2, int(2 * s)))
        # Гарда
        pygame.draw.line(surface, color,
                         (int(cx - 4 * s), int(cy - 1 * s)),
                         (int(cx + 1 * s), int(cy + 4 * s)), max(2, int(2 * s)))
        # Рукоять
        pygame.draw.line(surface, (180, 140, 100),
                         (int(cx - 7 * s), int(cy + 7 * s)),
                         (int(cx - 9 * s), int(cy + 9 * s)), max(3, int(3 * s)))

    @staticmethod
    def draw_folder(surface, x, y, size=20, color=(220, 200, 255)):
        """Папка — для 'Загрузить игру'."""
        s = size / 20
        # Корпус
        rect = pygame.Rect(int(x + 2 * s), int(y + 5 * s),
                           int(16 * s), int(12 * s))
        pygame.draw.rect(surface, color, rect, max(2, int(2 * s)), border_radius=2)
        # Ушко
        tab = pygame.Rect(int(x + 2 * s), int(y + 3 * s),
                          int(7 * s), int(4 * s))
        pygame.draw.rect(surface, color, tab, max(2, int(2 * s)), border_radius=1)

    @staticmethod
    def draw_trophy(surface, x, y, size=20, color=(255, 200, 50)):
        """Кубок — для 'Достижения'."""
        s = size / 20
        cx = x + size // 2

        # Чаша
        points = [
            (int(cx - 6 * s), int(y + 3 * s)),
            (int(cx + 6 * s), int(y + 3 * s)),
            (int(cx + 4 * s), int(y + 10 * s)),
            (int(cx - 4 * s), int(y + 10 * s)),
        ]
        pygame.draw.polygon(surface, color, points, max(2, int(2 * s)))

        # Ножка
        pygame.draw.line(surface, color,
                         (int(cx), int(y + 10 * s)),
                         (int(cx), int(y + 14 * s)), max(2, int(2 * s)))
        # База
        pygame.draw.line(surface, color,
                         (int(cx - 4 * s), int(y + 14 * s)),
                         (int(cx + 4 * s), int(y + 14 * s)), max(2, int(2 * s)))

        # Ручки
        pygame.draw.arc(surface, color,
                        pygame.Rect(int(cx - 9 * s), int(y + 3 * s),
                                    int(5 * s), int(6 * s)),
                        -1.5, 1.5, max(2, int(2 * s)))
        pygame.draw.arc(surface, color,
                        pygame.Rect(int(cx + 4 * s), int(y + 3 * s),
                                    int(5 * s), int(6 * s)),
                        1.5, 4.7, max(2, int(2 * s)))

    @staticmethod
    def draw_gear(surface, x, y, size=20, color=(220, 200, 255)):
        """Шестерёнка — для 'Настройки'."""
        cx = x + size // 2
        cy = y + size // 2
        s = size / 20

        outer_r = int(8 * s)
        inner_r = int(5 * s)
        teeth = 6

        # Зубцы
        points = []
        for i in range(teeth * 2):
            angle = math.pi * 2 * i / (teeth * 2) - math.pi / 2
            r = outer_r if i % 2 == 0 else inner_r
            px = cx + int(r * math.cos(angle))
            py = cy + int(r * math.sin(angle))
            points.append((px, py))

        if len(points) >= 3:
            pygame.draw.polygon(surface, color, points, max(2, int(2 * s)))

        # Центральный круг
        pygame.draw.circle(surface, color, (cx, cy), int(3 * s), max(2, int(2 * s)))

    @staticmethod
    def draw_door(surface, x, y, size=20, color=(220, 200, 255)):
        """Дверь — для 'Выход'."""
        s = size / 20

        # Рамка двери
        door_rect = pygame.Rect(int(x + 4 * s), int(y + 2 * s),
                                int(10 * s), int(16 * s))
        pygame.draw.rect(surface, color, door_rect, max(2, int(2 * s)), border_radius=1)

        # Ручка
        pygame.draw.circle(surface, color,
                           (int(x + 12 * s), int(y + 10 * s)), max(2, int(2 * s)))

        # Стрелка выхода
        arrow_x = int(x + 15 * s)
        arrow_y = int(y + 10 * s)
        pygame.draw.line(surface, color,
                         (arrow_x, arrow_y),
                         (int(arrow_x + 4 * s), arrow_y), max(2, int(2 * s)))
        pygame.draw.line(surface, color,
                         (int(arrow_x + 4 * s), arrow_y),
                         (int(arrow_x + 2 * s), int(arrow_y - 2 * s)), max(1, int(1 * s)))
        pygame.draw.line(surface, color,
                         (int(arrow_x + 4 * s), arrow_y),
                         (int(arrow_x + 2 * s), int(arrow_y + 2 * s)), max(1, int(1 * s)))

    @staticmethod
    def draw_save(surface, x, y, size=20, color=(60, 200, 120)):
        """Дискета — для 'Сохранить'."""
        s = size / 20
        # Корпус
        rect = pygame.Rect(int(x + 2 * s), int(y + 2 * s),
                           int(16 * s), int(16 * s))
        pygame.draw.rect(surface, color, rect, max(2, int(2 * s)), border_radius=2)
        # Экран
        inner = pygame.Rect(int(x + 5 * s), int(y + 9 * s),
                            int(10 * s), int(7 * s))
        pygame.draw.rect(surface, color, inner, max(1, int(1 * s)))
        # Затвор
        top = pygame.Rect(int(x + 6 * s), int(y + 2 * s),
                          int(7 * s), int(5 * s))
        pygame.draw.rect(surface, color, top, max(1, int(1 * s)))

    @staticmethod
    def draw_cross(surface, x, y, size=20, color=(220, 60, 60)):
        """Крестик — для 'Закрыть'."""
        cx = x + size // 2
        cy = y + size // 2
        s = size / 20
        d = int(6 * s)
        w = max(2, int(2 * s))
        pygame.draw.line(surface, color, (cx - d, cy - d), (cx + d, cy + d), w)
        pygame.draw.line(surface, color, (cx + d, cy - d), (cx - d, cy + d), w)

    @staticmethod
    def draw_monitor(surface, x, y, size=20, color=(220, 200, 255)):
        """Монитор — для вкладки 'Видео'."""
        s = size / 20
        # Экран
        screen_rect = pygame.Rect(int(x + 2 * s), int(y + 2 * s),
                                  int(16 * s), int(11 * s))
        pygame.draw.rect(surface, color, screen_rect, max(2, int(2 * s)), border_radius=2)
        # Ножка
        pygame.draw.line(surface, color,
                         (int(x + 10 * s), int(y + 13 * s)),
                         (int(x + 10 * s), int(y + 16 * s)), max(2, int(2 * s)))
        # Подставка
        pygame.draw.line(surface, color,
                         (int(x + 6 * s), int(y + 16 * s)),
                         (int(x + 14 * s), int(y + 16 * s)), max(2, int(2 * s)))

    @staticmethod
    def draw_speaker(surface, x, y, size=20, color=(220, 200, 255)):
        """Динамик — для вкладки 'Аудио'."""
        s = size / 20
        # Корпус
        body = pygame.Rect(int(x + 3 * s), int(y + 6 * s),
                           int(5 * s), int(8 * s))
        pygame.draw.rect(surface, color, body)
        # Раструб
        points = [
            (int(x + 8 * s), int(y + 6 * s)),
            (int(x + 13 * s), int(y + 2 * s)),
            (int(x + 13 * s), int(y + 18 * s)),
            (int(x + 8 * s), int(y + 14 * s)),
        ]
        pygame.draw.polygon(surface, color, points)
        # Волны
        for i in range(2):
            r = int((4 + i * 3) * s)
            rect = pygame.Rect(int(x + 13 * s) - r, int(y + 10 * s) - r, r * 2, r * 2)
            pygame.draw.arc(surface, color, rect, -0.8, 0.8, max(1, int(2 * s)))

    @staticmethod
    def draw_gamepad(surface, x, y, size=20, color=(220, 200, 255)):
        """Геймпад — для вкладки 'Управление'."""
        s = size / 20
        cx = x + size // 2
        cy = y + size // 2

        # Корпус
        body = pygame.Rect(int(x + 2 * s), int(y + 5 * s),
                           int(16 * s), int(10 * s))
        pygame.draw.rect(surface, color, body, max(2, int(2 * s)), border_radius=int(4 * s))

        # D-pad
        dp_x, dp_y = int(x + 7 * s), int(cy)
        dp_s = max(1, int(2 * s))
        pygame.draw.line(surface, color,
                         (dp_x - int(2 * s), dp_y), (dp_x + int(2 * s), dp_y), dp_s)
        pygame.draw.line(surface, color,
                         (dp_x, dp_y - int(2 * s)), (dp_x, dp_y + int(2 * s)), dp_s)

        # Кнопки
        btn_x = int(x + 14 * s)
        pygame.draw.circle(surface, color, (btn_x, int(cy - 2 * s)), max(1, int(1.5 * s)))
        pygame.draw.circle(surface, color, (btn_x, int(cy + 2 * s)), max(1, int(1.5 * s)))

    @staticmethod
    def draw_reset(surface, x, y, size=20, color=(220, 200, 255)):
        """Стрелка сброса — для 'Сбросить'."""
        cx = x + size // 2
        cy = y + size // 2
        s = size / 20
        r = int(6 * s)
        w = max(2, int(2 * s))

        # Дуга
        rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
        pygame.draw.arc(surface, color, rect, 0.5, 5.5, w)

        # Стрелка на конце
        angle = 0.5
        tip_x = cx + int(r * math.cos(angle))
        tip_y = cy - int(r * math.sin(angle))
        pygame.draw.line(surface, color,
                         (tip_x, tip_y), (tip_x + int(3 * s), tip_y), w)
        pygame.draw.line(surface, color,
                         (tip_x, tip_y), (tip_x, tip_y + int(3 * s)), w)