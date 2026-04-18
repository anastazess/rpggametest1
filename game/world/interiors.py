import pygame
import random
from dataclasses import dataclass, field
from typing import List, Tuple
from game.constants import *
from game.world.npc import (NPC, create_blacksmith, create_merchant,
                            create_innkeeper, create_guild_master,
                            create_barmaid, create_villager, NPCAppearance)


@dataclass
class Furniture:
    """Мебель / объект интерьера."""
    x: int
    y: int
    width: int
    height: int
    name: str
    color: tuple
    is_solid: bool = True
    interaction: str = ""  # "sit", "examine", "use"
    detail_color: tuple = None


class Interior:
    """Базовый класс интерьера здания."""

    def __init__(self, name: str, width: int = 400, height: int = 320):
        self.name = name
        self.width = width
        self.height = height

        self.floor_color = (60, 50, 45)
        self.wall_color = (80, 70, 60)
        self.trim_color = (100, 80, 60)

        self.furniture: List[Furniture] = []
        self.npcs: List[NPC] = []
        self.colliders: List[pygame.Rect] = []

        self.entry_point = (width // 2, height - 40)

        self._generate()

    def _generate(self):
        """Переопределить в подклассах."""
        pass

    def _add_walls(self):
        """Добавить коллайдеры стен."""
        wall_thickness = 20
        # Верхняя стена
        self.colliders.append(pygame.Rect(0, 0, self.width, wall_thickness))
        # Левая стена
        self.colliders.append(pygame.Rect(0, 0, wall_thickness, self.height))
        # Правая стена
        self.colliders.append(pygame.Rect(self.width - wall_thickness, 0,
                                          wall_thickness, self.height))
        # Нижняя стена (с проёмом двери)
        door_width = 50
        door_x = self.width // 2 - door_width // 2
        self.colliders.append(pygame.Rect(0, self.height - wall_thickness,
                                          door_x, wall_thickness))
        self.colliders.append(pygame.Rect(door_x + door_width, self.height - wall_thickness,
                                          self.width - door_x - door_width, wall_thickness))

    def add_furniture(self, furn: Furniture):
        self.furniture.append(furn)
        if furn.is_solid:
            self.colliders.append(pygame.Rect(furn.x, furn.y, furn.width, furn.height))

    def get_ground(self) -> pygame.Surface:
        """Генерирует поверхность пола и стен."""
        surf = pygame.Surface((self.width, self.height))

        # Пол
        surf.fill(self.floor_color)

        # Паттерн пола
        tile_size = 40
        for tx in range(0, self.width, tile_size):
            for ty in range(0, self.height, tile_size):
                if (tx // tile_size + ty // tile_size) % 2 == 0:
                    darker = tuple(max(0, c - 8) for c in self.floor_color)
                    pygame.draw.rect(surf, darker, (tx, ty, tile_size, tile_size))

        # Стены
        wall_h = 25
        pygame.draw.rect(surf, self.wall_color, (0, 0, self.width, wall_h))
        pygame.draw.rect(surf, self.trim_color, (0, wall_h - 3, self.width, 3))

        # Боковые стены (тень)
        pygame.draw.rect(surf, tuple(max(0, c - 15) for c in self.floor_color),
                         (0, 0, 15, self.height))
        pygame.draw.rect(surf, tuple(max(0, c - 15) for c in self.floor_color),
                         (self.width - 15, 0, 15, self.height))

        return surf

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        """Отрисовка мебели."""
        for furn in self.furniture:
            self._draw_furniture(surface, furn, camera_x, camera_y)

    def _draw_furniture(self, surface: pygame.Surface, furn: Furniture,
                        camera_x: float, camera_y: float):
        fx = int(furn.x - camera_x)
        fy = int(furn.y - camera_y)

        # Тень
        shadow = pygame.Surface((furn.width + 4, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 40), (0, 0, furn.width + 4, 8))
        surface.blit(shadow, (fx - 2, fy + furn.height - 4))

        # Основа
        pygame.draw.rect(surface, furn.color,
                         (fx, fy, furn.width, furn.height), border_radius=3)

        # Грань (3D эффект)
        lighter = tuple(min(255, c + 30) for c in furn.color)
        pygame.draw.rect(surface, lighter,
                         (fx, fy, furn.width, 5), border_radius=3)

        darker = tuple(max(0, c - 30) for c in furn.color)
        pygame.draw.rect(surface, darker,
                         (fx, fy, furn.width, furn.height), width=1, border_radius=3)

        # Детали
        if furn.detail_color:
            pygame.draw.rect(surface, furn.detail_color,
                             (fx + 3, fy + 3, furn.width - 6, furn.height - 6),
                             border_radius=2)

    def update(self, dt: float, player_rect: pygame.Rect):
        for npc in self.npcs:
            npc.update(dt, player_rect)

    def draw_npcs(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        # Сортируем по Y для правильного перекрытия
        sorted_npcs = sorted(self.npcs, key=lambda n: n.y)
        for npc in sorted_npcs:
            npc.draw(surface, camera_x, camera_y)

    def get_hovered_npc(self) -> NPC:
        for npc in self.npcs:
            if npc.hovered:
                return npc
        return None


class BlacksmithInterior(Interior):
    """Интерьер кузницы."""

    def __init__(self):
        super().__init__("Кузница", 350, 280)
        self.floor_color = (50, 45, 40)
        self.wall_color = (70, 60, 55)

    def _generate(self):
        self._add_walls()

        # Горн (печь)
        self.add_furniture(Furniture(
            20, 30, 80, 60, "Горн",
            (60, 40, 35), detail_color=(255, 120, 50)
        ))

        # Наковальня
        self.add_furniture(Furniture(
            150, 100, 50, 35, "Наковальня",
            (100, 100, 105)
        ))

        # Бочка с водой
        self.add_furniture(Furniture(
            260, 40, 40, 45, "Бочка",
            (80, 60, 45), detail_color=(80, 120, 180)
        ))

        # Стеллаж с оружием
        self.add_furniture(Furniture(
            250, 120, 70, 40, "Стеллаж",
            (90, 70, 55)
        ))

        # Рабочий стол
        self.add_furniture(Furniture(
            30, 150, 90, 45, "Рабочий стол",
            (100, 75, 55)
        ))

        # Ящик с углём
        self.add_furniture(Furniture(
            120, 30, 35, 30, "Ящик с углём",
            (40, 35, 35)
        ))

        # NPC - кузнец
        blacksmith = create_blacksmith()
        blacksmith.x = 150
        blacksmith.y = 150
        self.npcs.append(blacksmith)

        self.entry_point = (self.width // 2, self.height - 50)


class ShopInterior(Interior):
    """Интерьер магазина."""

    def __init__(self):
        super().__init__("Магазин", 380, 300)
        self.floor_color = (65, 55, 50)
        self.wall_color = (90, 80, 70)

    def _generate(self):
        self._add_walls()

        # Прилавок
        self.add_furniture(Furniture(
            100, 80, 180, 35, "Прилавок",
            (100, 80, 60)
        ))

        # Полки слева
        for i in range(3):
            self.add_furniture(Furniture(
                20, 40 + i * 55, 60, 45, f"Полка {i + 1}",
                (90, 75, 60)
            ))

        # Полки справа
        for i in range(3):
            self.add_furniture(Furniture(
                300, 40 + i * 55, 60, 45, f"Полка {i + 4}",
                (90, 75, 60)
            ))

        # Бочки
        self.add_furniture(Furniture(
            130, 200, 35, 40, "Бочка",
            (85, 65, 50)
        ))
        self.add_furniture(Furniture(
            215, 200, 35, 40, "Бочка",
            (85, 65, 50)
        ))

        # Сундук
        self.add_furniture(Furniture(
            270, 200, 50, 35, "Сундук",
            (100, 70, 45), detail_color=(180, 150, 50)
        ))

        # NPC - торговец
        merchant = create_merchant()
        merchant.x = 170
        merchant.y = 35
        self.npcs.append(merchant)

        self.entry_point = (self.width // 2, self.height - 50)


class TavernInterior(Interior):
    """Интерьер таверны."""

    def __init__(self):
        super().__init__("Таверна", 450, 350)
        self.floor_color = (55, 45, 40)
        self.wall_color = (85, 70, 60)

    def _generate(self):
        self._add_walls()

        # Барная стойка
        self.add_furniture(Furniture(
            280, 50, 150, 40, "Стойка",
            (90, 70, 55)
        ))

        # Столы
        table_positions = [(50, 80), (50, 180), (160, 130), (160, 230)]
        for i, (tx, ty) in enumerate(table_positions):
            self.add_furniture(Furniture(
                tx, ty, 70, 50, f"Стол {i + 1}",
                (95, 75, 55)
            ))

        # Стулья (декоративные, не solid)
        for tx, ty in table_positions:
            for offset in [(0, -20), (0, 55), (-25, 15), (70, 15)]:
                self.furniture.append(Furniture(
                    tx + 25 + offset[0], ty + offset[1], 20, 20, "Стул",
                    (80, 65, 50), is_solid=False
                ))

        # Камин
        self.add_furniture(Furniture(
            20, 30, 60, 50, "Камин",
            (70, 55, 50), detail_color=(255, 150, 50)
        ))

        # Бочки за стойкой
        for i in range(3):
            self.add_furniture(Furniture(
                290 + i * 45, 20, 35, 25, f"Бочка эля {i + 1}",
                (80, 60, 45)
            ))

        # Лестница наверх
        self.add_furniture(Furniture(
            380, 200, 50, 80, "Лестница",
            (100, 80, 60)
        ))

        # NPCs
        innkeeper = create_innkeeper()
        innkeeper.x = 330
        innkeeper.y = 90
        self.npcs.append(innkeeper)

        barmaid = create_barmaid()
        barmaid.x = 280
        barmaid.y = 100
        self.npcs.append(barmaid)

        # Посетители
        patron1 = create_villager("Посетитель Рик")
        patron1.x = 70
        patron1.y = 130
        self.npcs.append(patron1)

        patron2 = create_villager("Посетитель Ян")
        patron2.x = 180
        patron2.y = 180
        self.npcs.append(patron2)

        self.entry_point = (self.width // 2, self.height - 50)


class GuildInterior(Interior):
    """Интерьер гильдии."""

    def __init__(self):
        super().__init__("Гильдия Искателей", 480, 380)
        self.floor_color = (55, 50, 60)
        self.wall_color = (75, 65, 80)
        self.trim_color = (100, 85, 110)

    def _generate(self):
        self._add_walls()

        # Стойка регистрации — НЕ solid чтобы не блокировать проход
        self.furniture.append(Furniture(
            150, 60, 180, 35, "Стойка регистрации",
            (85, 70, 95), is_solid=False
        ))
        # Коллайдер только для верхней части стойки
        self.colliders.append(pygame.Rect(150, 60, 180, 20))

        # Доска объявлений
        self.add_furniture(Furniture(
            30, 30, 80, 65, "Доска объявлений",
            (100, 80, 65)
        ))

        # Трофейная витрина
        self.add_furniture(Furniture(
            370, 30, 90, 95, "Трофеи",
            (90, 75, 100), detail_color=(200, 180, 100)
        ))

        # Большие столы — с проходами между ними
        self.add_furniture(Furniture(
            40, 190, 110, 55, "Стол искателей",
            (90, 75, 80)
        ))
        self.add_furniture(Furniture(
            200, 190, 110, 55, "Стол заданий",
            (90, 75, 80)
        ))
        self.add_furniture(Furniture(
            330, 190, 110, 55, "Стол архива",
            (90, 75, 80)
        ))

        # Книжный шкаф у правой стены
        self.add_furniture(Furniture(
            440, 160, 25, 120, "Книжный шкаф",
            (85, 70, 65)
        ))

        # Стойка с оружием у левой стены
        self.add_furniture(Furniture(
            20, 160, 15, 80, "Стойка с оружием",
            (80, 70, 75)
        ))

        # Декоративные кресла (не solid)
        for cx in [50, 110, 210, 270, 340, 400]:
            self.furniture.append(Furniture(
                cx, 155, 28, 28, "Кресло",
                (100, 80, 90), is_solid=False
            ))

        # NPC — магистр за стойкой
        guild_master = create_guild_master()
        guild_master.x = 240
        guild_master.y = 20
        self.npcs.append(guild_master)

        # Искатели за столами
        seeker1 = create_villager("Искатель Марк")
        seeker1.x = 55
        seeker1.y = 260
        self.npcs.append(seeker1)

        seeker2 = create_villager("Искатель Эва")
        seeker2.x = 215
        seeker2.y = 260
        self.npcs.append(seeker2)

        seeker3 = create_villager("Искатель Дорн")
        seeker3.x = 345
        seeker3.y = 260
        self.npcs.append(seeker3)

        self.entry_point = (self.width // 2, self.height - 55)


class TempleInterior(Interior):
    """Величественный интерьер храма богини Авэлин."""

    def __init__(self):
        # Большой интерьер
        super().__init__("Храм Авэлин", 650, 550)
        self.floor_color = (75, 70, 95)
        self.wall_color = (100, 90, 120)
        self.trim_color = (140, 125, 165)

    def get_ground(self) -> pygame.Surface:
        """Красивый мраморный пол."""
        surf = pygame.Surface((self.width, self.height))

        # Базовый цвет
        surf.fill(self.floor_color)

        # Мраморный узор — шахматка с градиентом
        tile_size = 50
        for tx in range(0, self.width, tile_size):
            for ty in range(0, self.height, tile_size):
                if (tx // tile_size + ty // tile_size) % 2 == 0:
                    tile_col = (85, 78, 105)
                else:
                    tile_col = (70, 65, 88)

                pygame.draw.rect(surf, tile_col,
                                 (tx, ty, tile_size - 1, tile_size - 1))

                # Лёгкие прожилки мрамора
                import random
                random.seed(tx * 1000 + ty)
                for _ in range(3):
                    vx = tx + random.randint(5, tile_size - 5)
                    vy = ty + random.randint(5, tile_size - 5)
                    vlen = random.randint(8, 20)
                    vcol = tuple(min(255, c + 15) for c in tile_col)
                    pygame.draw.line(surf, vcol,
                                     (vx, vy), (vx + vlen // 2, vy + vlen), 1)

        # Центральная красная ковровая дорожка
        carpet_w = 80
        carpet_x = self.width // 2 - carpet_w // 2
        pygame.draw.rect(surf, (120, 40, 50),
                         (carpet_x, 60, carpet_w, self.height - 60))
        # Орнамент по краям ковра
        for oy in range(70, self.height - 20, 40):
            pygame.draw.rect(surf, (160, 70, 80),
                             (carpet_x + 5, oy, 10, 20))
            pygame.draw.rect(surf, (160, 70, 80),
                             (carpet_x + carpet_w - 15, oy, 10, 20))

        # Стена сверху с фреской
        wall_h = 40
        pygame.draw.rect(surf, self.wall_color,
                         (0, 0, self.width, wall_h))

        # Фреска богини (простое изображение)
        fresco_x = self.width // 2 - 60
        fresco_y = 5
        pygame.draw.rect(surf, (130, 115, 150),
                         (fresco_x, fresco_y, 120, 30), border_radius=3)
        # Силуэт богини
        pygame.draw.circle(surf, (200, 180, 220),
                           (fresco_x + 60, fresco_y + 12), 10)
        pygame.draw.polygon(surf, (200, 180, 220),
                            [(fresco_x + 50, fresco_y + 18),
                             (fresco_x + 70, fresco_y + 18),
                             (fresco_x + 60, fresco_y + 30)])

        # Бордюр
        pygame.draw.rect(surf, self.trim_color,
                         (0, wall_h - 4, self.width, 4))

        # Боковые тени стен
        for sx in [0, self.width - 20]:
            for sy in range(0, self.height, 2):
                alpha = max(0, 60 - sy // 10)
                col = tuple(max(0, self.floor_color[i] - 15) for i in range(3))
                pygame.draw.line(surf, col, (sx, sy), (sx + 20, sy))

        return surf

    def _generate(self):
        self._add_walls()

        # ══════════════════════════════════════════════════════════════
        # АЛТАРЬ — центральный, величественный
        # ══════════════════════════════════════════════════════════════

        # Основание алтаря (ступенчатое)
        self.add_furniture(Furniture(
            220, 45, 210, 30, "Основание алтаря",
            (160, 150, 175)
        ))
        # Сам алтарь
        self.add_furniture(Furniture(
            250, 30, 150, 45, "Священный алтарь Авэлин",
            (180, 165, 200), detail_color=(255, 240, 200)
        ))

        # Большие подсвечники по бокам алтаря
        for cx in [200, 440]:
            self.add_furniture(Furniture(
                cx, 40, 20, 50, "Священный подсвечник",
                (180, 160, 140), detail_color=(255, 200, 80)
            ))

        # Чаша с благовониями
        self.furniture.append(Furniture(
            310, 55, 30, 20, "Чаша благовоний",
            (200, 180, 160), is_solid=False,
            detail_color=(220, 200, 150)
        ))

        # ══════════════════════════════════════════════════════════════
        # КОЛОННЫ — два ряда
        # ══════════════════════════════════════════════════════════════

        col_y_positions = [130, 230, 330, 430]

        # Левый ряд колонн
        for cy in col_y_positions:
            self.add_furniture(Furniture(
                50, cy, 25, 25, "Мраморная колонна",
                (180, 170, 195)
            ))

        # Правый ряд колонн
        for cy in col_y_positions:
            self.add_furniture(Furniture(
                575, cy, 25, 25, "Мраморная колонна",
                (180, 170, 195)
            ))

        # ══════════════════════════════════════════════════════════════
        # СКАМЬИ — три ряда с двух сторон
        # ══════════════════════════════════════════════════════════════

        bench_rows = [(160, 200), (260, 300), (360, 400)]

        for start_y, end_y in bench_rows:
            # Левая скамья
            self.add_furniture(Furniture(
                90, start_y, 170, 35, "Скамья для молящихся",
                (110, 95, 85)
            ))
            # Правая скамья
            self.add_furniture(Furniture(
                390, start_y, 170, 35, "Скамья для молящихся",
                (110, 95, 85)
            ))

        # ══════════════════════════════════════════════════════════════
        # БОКОВЫЕ АЛТАРИ / НИШИ
        # ══════════════════════════════════════════════════════════════

        # Левая ниша — статуя
        self.add_furniture(Furniture(
            25, 100, 40, 50, "Статуя Предвестницы",
            (170, 160, 185), detail_color=(200, 190, 210)
        ))

        # Правая ниша — статуя
        self.add_furniture(Furniture(
            585, 100, 40, 50, "Статуя Хранительницы",
            (170, 160, 185), detail_color=(200, 190, 210)
        ))

        # Столики с подношениями
        self.add_furniture(Furniture(
            25, 200, 35, 30, "Стол подношений",
            (130, 115, 100)
        ))
        self.add_furniture(Furniture(
            590, 200, 35, 30, "Стол подношений",
            (130, 115, 100)
        ))

        # ══════════════════════════════════════════════════════════════
        # ВИТРАЖИ (декоративные, не solid)
        # ══════════════════════════════════════════════════════════════

        # Большой витраж над алтарём (на стене — рисуем в get_ground)

        # Боковые витражи
        for vy, vcol in [(120, (180, 130, 200)), (220, (130, 180, 200)),
                         (320, (200, 180, 130)), (420, (130, 200, 160))]:
            self.furniture.append(Furniture(
                20, vy, 8, 35, "Витраж",
                vcol, is_solid=False
            ))
            self.furniture.append(Furniture(
                622, vy, 8, 35, "Витраж",
                vcol, is_solid=False
            ))

        # ══════════════════════════════════════════════════════════════
        # СВЕЧИ (декоративные)
        # ══════════════════════════════════════════════════════════════

        candle_positions = [
            (100, 140), (180, 140), (470, 140), (550, 140),
            (100, 350), (180, 350), (470, 350), (550, 350),
        ]
        for cx, cy in candle_positions:
            self.furniture.append(Furniture(
                cx, cy, 12, 18, "Свеча",
                (220, 200, 160), is_solid=False,
                detail_color=(255, 220, 100)
            ))

        # ══════════════════════════════════════════════════════════════
        # КУПЕЛЬ (слева от входа)
        # ══════════════════════════════════════════════════════════════

        self.add_furniture(Furniture(
            100, 450, 50, 50, "Священная купель",
            (160, 150, 175), detail_color=(150, 180, 220)
        ))

        # ══════════════════════════════════════════════════════════════
        # БИБЛИОТЕКА МОЛИТВ (справа от входа)
        # ══════════════════════════════════════════════════════════════

        self.add_furniture(Furniture(
            500, 440, 80, 60, "Книжный шкаф молитв",
            (100, 85, 75)
        ))

        # ══════════════════════════════════════════════════════════════
        # NPC — ИЕРАРХИЯ ХРАМА
        # ══════════════════════════════════════════════════════════════

        # 1. Верховная жрица — у алтаря
        high_priestess = self._create_high_priestess()
        high_priestess.x = 305
        high_priestess.y = 90
        self.npcs.append(high_priestess)

        # 2. Старшие сёстры — по бокам от алтаря
        sister1 = self._create_elder_sister("Старшая сестра Мирея",
                                            "Я отвечаю за ритуалы исцеления.")
        sister1.x = 220
        sister1.y = 100
        self.npcs.append(sister1)

        sister2 = self._create_elder_sister("Старшая сестра Орина",
                                            "Богиня видит твои помыслы, путник.")
        sister2.x = 400
        sister2.y = 100
        self.npcs.append(sister2)

        # 3. Жрицы у боковых алтарей
        priestess1 = self._create_priestess("Жрица Элана")
        priestess1.x = 40
        priestess1.y = 170
        self.npcs.append(priestess1)

        priestess2 = self._create_priestess("Жрица Сельма")
        priestess2.x = 590
        priestess2.y = 170
        self.npcs.append(priestess2)

        # 4. Послушницы — у скамей, помогают прихожанам
        novice1 = self._create_novice("Послушница Лия")
        novice1.x = 130
        novice1.y = 260
        self.npcs.append(novice1)

        novice2 = self._create_novice("Послушница Вера")
        novice2.x = 490
        novice2.y = 260
        self.npcs.append(novice2)

        novice3 = self._create_novice("Послушница Ирис")
        novice3.x = 130
        novice3.y = 360
        self.npcs.append(novice3)

        novice4 = self._create_novice("Послушница Альма")
        novice4.x = 490
        novice4.y = 360
        self.npcs.append(novice4)

        # 5. Хранительница знаний — у книжного шкафа
        keeper = self._create_lore_keeper()
        keeper.x = 520
        keeper.y = 420
        self.npcs.append(keeper)

        # 6. Сестра у купели
        baptizer = self._create_baptizer()
        baptizer.x = 110
        baptizer.y = 420
        self.npcs.append(baptizer)

        # 7. Молящиеся прихожане (жители)
        from game.world.npc import create_villager

        worshipper1 = create_villager("Молящийся крестьянин")
        worshipper1.x = 140
        worshipper1.y = 180
        self.npcs.append(worshipper1)

        worshipper2 = create_villager("Молящаяся женщина")
        worshipper2.x = 430
        worshipper2.y = 180
        self.npcs.append(worshipper2)

        worshipper3 = create_villager("Скорбящий вдовец")
        worshipper3.x = 200
        worshipper3.y = 280
        self.npcs.append(worshipper3)

        self.entry_point = (self.width // 2, self.height - 60)

    # ══════════════════════════════════════════════════════════════════
    # СОЗДАТЕЛИ NPC
    # ══════════════════════════════════════════════════════════════════

    def _create_high_priestess(self) -> NPC:
        """Верховная жрица храма."""
        appearance = NPCAppearance(
            body_color=(140, 120, 180),
            skin_color=(235, 210, 195),
            hair_color=(220, 215, 230),  # седые/белые
            hair_style="long",
            outfit_color=(160, 140, 200),
            has_beard=False,
            has_hat=False,
            accessory="hood",
        )
        dialogues = [
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "Добро пожаловать в храм Авэлин, богини рассвета, исцеления и вечного света.",
             "portrait_color": (200, 170, 230)},
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "Авэлин хранит равновесие между светом и тьмой. Без неё мир давно бы погиб во мраке.",
             "portrait_color": (200, 170, 230)},
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "Я чувствую в тебе искру... Ты пришёл из-за Завесы, не так ли? Немногие выживают в том путешествии.",
             "portrait_color": (200, 170, 230)},
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "Если хочешь получить благословение Авэлин — принеси к алтарю три лунных цветка. Они растут в Туманном лесу в полнолуние.",
             "portrait_color": (200, 170, 230)},
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "А пока — отдохни. Сёстры позаботятся о тебе. Свет богини да пребудет с тобой.",
             "portrait_color": (200, 170, 230)},
        ]
        npc = NPC(0, 0, "Верховная жрица Иссара",
                   appearance, dialogues, "high_priestess")
        npc.appearance = appearance  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        return npc

    def _create_elder_sister(self, name: str, special_text: str) -> NPC:
        """Старшая сестра храма."""
        appearance = NPCAppearance(
            body_color=(120, 105, 155),
            skin_color=(230, 200, 185),
            hair_color=(180, 170, 190),
            hair_style="ponytail",
            outfit_color=(135, 118, 170),
            has_beard=False,
            accessory="hood",
        )
        dialogues = [
            {"speaker": name,
             "role": "Старшая сестра храма Авэлин",
             "text": "Да осенит тебя благодать Авэлин, путник.",
             "portrait_color": (180, 155, 210)},
            {"speaker": name,
             "role": "Старшая сестра храма Авэлин",
             "text": special_text,
             "portrait_color": (180, 155, 210)},
            {"speaker": name,
             "role": "Старшая сестра храма Авэлин",
             "text": "Если тебе нужно исцеление — оставь подношение на алтаре, и богиня услышит твою молитву.",
             "portrait_color": (180, 155, 210)},
        ]
        npc = NPC(0, 0, name, appearance, dialogues, "elder_sister")
        npc.appearance = appearance  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        return npc

    def _create_priestess(self, name: str) -> NPC:
        """Жрица у боковых алтарей."""
        import random
        appearance = NPCAppearance(
            body_color=(115, 100, 145),
            skin_color=(225, 195, 175),
            hair_color=(random.randint(120, 200),
                        random.randint(100, 160),
                        random.randint(80, 140)),
            hair_style=random.choice(["long", "ponytail"]),
            outfit_color=(125, 108, 155),
            has_beard=False,
            accessory="hood",
        )
        dialogues = [
            {"speaker": name,
             "role": "Жрица храма Авэлин",
             "text": "Этот алтарь посвящён одному из ликов богини. Авэлин многолика, как и сама жизнь.",
             "portrait_color": (165, 145, 195)},
            {"speaker": name,
             "role": "Жрица храма Авэлин",
             "text": "Оставь здесь цветок или свечу — и она услышит тебя.",
             "portrait_color": (165, 145, 195)},
        ]
        npc = NPC(0, 0, name, appearance, dialogues, "priestess")
        npc.appearance = appearance  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        return npc

    def _create_novice(self, name: str) -> NPC:
        """Послушница храма."""
        import random
        appearance = NPCAppearance(
            body_color=(105, 92, 130),
            skin_color=(235, 205, 185),
            hair_color=(random.randint(80, 180),
                        random.randint(60, 140),
                        random.randint(40, 100)),
            hair_style=random.choice(["long", "ponytail", "short"]),
            outfit_color=(115, 100, 140),
            has_beard=False,
            accessory="",
        )
        dialogues = [
            {"speaker": name,
             "role": "Послушница храма Авэлин",
             "text": "Да пребудет с тобой свет Авэлин!",
             "portrait_color": (155, 135, 185)},
            {"speaker": name,
             "role": "Послушница храма Авэлин",
             "text": random.choice([
                 "Я пришла в храм два года назад. Это лучшее решение в моей жизни.",
                 "Мы молимся каждый рассвет. Присоединяйся, если хочешь.",
                 "Богиня учит нас милосердию и терпению.",
                 "Старшие сёстры строги, но справедливы.",
                 "Скоро я сдам испытание и стану полноправной жрицей!",
             ]),
             "portrait_color": (155, 135, 185)},
        ]
        npc = NPC(0, 0, name, appearance, dialogues, "novice")
        npc.appearance = appearance  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        return npc

    def _create_lore_keeper(self) -> NPC:
        """Хранительница знаний."""
        appearance = NPCAppearance(
            body_color=(100, 90, 120),
            skin_color=(220, 190, 170),
            hair_color=(100, 90, 85),
            hair_style="ponytail",
            outfit_color=(110, 98, 130),
            has_beard=False,
            accessory="",
        )
        dialogues = [
            {"speaker": "Тереза",
             "role": "Хранительница знаний храма",
             "text": "Тише... Это библиотека священных текстов. Здесь хранятся молитвы и пророчества тысячелетней давности.",
             "portrait_color": (150, 130, 170)},
            {"speaker": "Тереза",
             "role": "Хранительница знаний храма",
             "text": "Если ищешь знания о Древних — я могу помочь. Но некоторые книги запечатаны не без причины...",
             "portrait_color": (150, 130, 170)},
            {"speaker": "Тереза",
             "role": "Хранительница знаний храма",
             "text": "Есть одно пророчество... о том, кто придёт из-за Завесы. Хочешь — прочту?",
             "portrait_color": (150, 130, 170)},
        ]
        npc = NPC(0, 0, "Хранительница Тереза",
                   appearance, dialogues, "lore_keeper")
        npc.appearance = appearance  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        return npc

    def _create_baptizer(self) -> NPC:
        """Сестра, проводящая обряды у купели."""
        appearance = NPCAppearance(
            body_color=(110, 100, 140),
            skin_color=(228, 198, 180),
            hair_color=(160, 140, 120),
            hair_style="long",
            outfit_color=(120, 108, 150),
            has_beard=False,
            accessory="",
        )
        dialogues = [
            {"speaker": "Агата",
             "role": "Сестра-целительница храма",
             "text": "Священная купель очищает душу от скверны. Многие приходят сюда после встречи с тьмой.",
             "portrait_color": (160, 145, 190)},
            {"speaker": "Агата",
             "role": "Сестра-целительница храма",
             "text": "Вода в купели благословлена самой Авэлин. Она снимает проклятия и исцеляет раны духа.",
             "portrait_color": (160, 145, 190)},
            {"speaker": "Агата",
             "role": "Сестра-целительница храма",
             "text": "Хочешь пройти обряд очищения? Это займёт немного времени, но ты почувствуешь себя обновлённым.",
             "portrait_color": (160, 145, 190)},
        ]
        npc = NPC(0, 0, "Сестра Агата",
                   appearance, dialogues, "baptizer")
        npc.appearance = appearance  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        return npc

    def _draw_furniture(self, surface: pygame.Surface, furn: Furniture,
                        camera_x: float, camera_y: float):
        """Переопределяем для красивых свечей."""
        fx = int(furn.x - camera_x)
        fy = int(furn.y - camera_y)

        # Свечи — особая отрисовка
        if "Свеча" in furn.name:
            # Подставка
            pygame.draw.rect(surface, (120, 100, 80),
                             (fx, fy + furn.height - 5, furn.width, 5))
            # Свеча
            pygame.draw.rect(surface, furn.color,
                             (fx + 2, fy + 5, furn.width - 4, furn.height - 10))
            # Пламя
            import math
            flame_y = fy + 3 + int(math.sin(pygame.time.get_ticks() / 150) * 1.5)
            pygame.draw.ellipse(surface, (255, 200, 50),
                                (fx + 3, flame_y, 6, 8))
            pygame.draw.ellipse(surface, (255, 255, 150),
                                (fx + 4, flame_y + 2, 4, 4))
            # Свечение
            glow = pygame.Surface((30, 30), pygame.SRCALPHA)
            glow_alpha = 40 + int(math.sin(pygame.time.get_ticks() / 200) * 15)
            pygame.draw.circle(glow, (255, 220, 100, glow_alpha), (15, 15), 14)
            surface.blit(glow, (fx - 9, fy - 8))
            return

        # Витражи — особая отрисовка
        if "Витраж" in furn.name:
            pygame.draw.rect(surface, (50, 45, 55),
                             (fx - 1, fy - 1, furn.width + 2, furn.height + 2))
            # Цветное стекло с градиентом
            for row in range(furn.height):
                ratio = row / furn.height
                r = int(furn.color[0] * (0.7 + 0.3 * ratio))
                g = int(furn.color[1] * (0.7 + 0.3 * ratio))
                b = int(furn.color[2] * (0.7 + 0.3 * ratio))
                pygame.draw.line(surface, (r, g, b),
                                 (fx, fy + row), (fx + furn.width, fy + row))
            # Лёгкое свечение
            import math
            glow_a = 30 + int(math.sin(pygame.time.get_ticks() / 400 + furn.y) * 10)
            glow = pygame.Surface((furn.width + 10, furn.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*furn.color, glow_a),
                             (0, 0, furn.width + 10, furn.height + 10))
            surface.blit(glow, (fx - 5, fy - 5))
            return

        # Священный подсвечник — особая отрисовка
        if "подсвечник" in furn.name.lower():
            # Основание
            pygame.draw.rect(surface, (100, 80, 60),
                             (fx, fy + furn.height - 10, furn.width, 10))
            # Ножка
            pygame.draw.rect(surface, furn.color,
                             (fx + 5, fy + 15, furn.width - 10, furn.height - 25))
            # Чаша для свечи
            pygame.draw.ellipse(surface, furn.color,
                                (fx, fy + 10, furn.width, 12))
            # Большое пламя
            import math
            ftime = pygame.time.get_ticks() / 120
            for i in range(3):
                fy_off = fy + 2 + int(math.sin(ftime + i) * 2)
                flame_w = 10 - i * 2
                flame_h = 14 - i * 3
                alpha = 255 - i * 40
                flame = pygame.Surface((flame_w, flame_h), pygame.SRCALPHA)
                colors = [(255, 180, 50, alpha), (255, 220, 100, alpha), (255, 255, 200, alpha)]
                pygame.draw.ellipse(flame, colors[i], (0, 0, flame_w, flame_h))
                surface.blit(flame, (fx + furn.width // 2 - flame_w // 2, fy_off))
            # Большое свечение
            glow = pygame.Surface((50, 50), pygame.SRCALPHA)
            glow_alpha = 50 + int(math.sin(ftime) * 15)
            pygame.draw.circle(glow, (255, 200, 80, glow_alpha), (25, 25), 22)
            surface.blit(glow, (fx - 15, fy - 15))
            return

        # Купель — особая отрисовка
        if "Купель" in furn.name:
            # Основание
            pygame.draw.ellipse(surface, (100, 90, 110),
                                (fx, fy + furn.height - 15, furn.width, 15))
            # Чаша
            pygame.draw.ellipse(surface, furn.color,
                                (fx, fy, furn.width, furn.height - 10))
            pygame.draw.ellipse(surface, tuple(c - 20 for c in furn.color),
                                (fx, fy, furn.width, furn.height - 10), width=2)
            # Вода
            water_y = fy + 8
            pygame.draw.ellipse(surface, furn.detail_color,
                                (fx + 5, water_y, furn.width - 10, furn.height - 25))
            # Рябь на воде
            import math
            ripple = int(math.sin(pygame.time.get_ticks() / 300) * 3)
            pygame.draw.ellipse(surface, (180, 210, 240),
                                (fx + 12 + ripple, water_y + 5, 8, 4))
            return

        # Стандартная отрисовка для остальных
        super()._draw_furniture(surface, furn, camera_x, camera_y)

# Фабрика интерьеров
def get_interior(building_name: str) -> Interior:
    mapping = {
        "Кузницу": BlacksmithInterior,
        "Магазин": ShopInterior,
        "Таверну": TavernInterior,
        "Гильдию": GuildInterior,
        "Храм": TempleInterior,
    }
    for key, cls in mapping.items():
        if key in building_name:
            return cls()

    return None