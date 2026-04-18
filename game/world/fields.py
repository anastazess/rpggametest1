import pygame
import random
import math
from game.constants import *


class FieldsMap:
    """Локация: Поля за стенами Валенхольма."""

    def __init__(self, width=2000, height=1600):
        self.width = width
        self.height = height
        self.name = "Поля Валенхольма"

        self.colliders = []
        self.decorations = []

        # Границы
        self.colliders.extend([
            pygame.Rect(-50, 0, 50, self.height),
            pygame.Rect(self.width, 0, 50, self.height),
            pygame.Rect(0, -50, self.width, 50),
            pygame.Rect(0, self.height, self.width, 50),
        ])

        # Дороги
        self.roads = [
            # Дорога из города (слева)
            pygame.Rect(0, 700, 500, 80),
            # Тропинка через поля
            pygame.Rect(500, 740, 800, 40),
            # Развилка вниз
            pygame.Rect(800, 780, 40, 400),
            # К мельнице
            pygame.Rect(1300, 400, 40, 380),
            # Тропа к лесу (правый край)
            pygame.Rect(1340, 400, 660, 40),
        ]

        self._generate_terrain()
        self._generate_decorations()
        self._generate_ground()

    # ── Ландшафт ─────────────────────────────────────────────────────

    def _generate_terrain(self):
        """Ограды, мельница, стога, камни."""
        random.seed(777)

        # ═══ Мельница ═══
        self.mill_x = 1250
        self.mill_y = 200
        self.colliders.append(pygame.Rect(self.mill_x + 15, self.mill_y + 50, 70, 80))

        # ═══ Фермерский дом ═══
        self.farmhouse = {"x": 400, "y": 400, "w": 110, "h": 90}
        self.colliders.append(pygame.Rect(400, 440, 110, 50))

        # ═══ Амбар ═══
        self.barn = {"x": 600, "y": 350, "w": 120, "h": 100}
        self.colliders.append(pygame.Rect(600, 400, 120, 50))

        # ═══ Колодец ═══
        self.well = {"x": 520, "y": 580}
        self.colliders.append(pygame.Rect(520, 580, 40, 40))

        # ═══ Заборы ═══
        self.fences = [
            pygame.Rect(350, 350, 5, 300),    # левая ограда
            pygame.Rect(350, 350, 400, 5),    # верхняя
            pygame.Rect(750, 350, 5, 300),    # правая
            pygame.Rect(350, 650, 400, 5),    # нижняя
        ]
        for f in self.fences:
            self.colliders.append(f)

        # ═══ Стога сена ═══
        self.haystacks = []
        for _ in range(8):
            hx = random.randint(100, 1800)
            hy = random.randint(100, 1400)
            on_road = any(r.collidepoint(hx, hy) for r in self.roads)
            in_farm = (350 < hx < 750 and 350 < hy < 650)
            if not on_road and not in_farm:
                self.haystacks.append({"x": hx, "y": hy, "size": random.randint(25, 40)})
                self.colliders.append(pygame.Rect(hx, hy + 10, 30, 15))

        # ═══ Пшеничные поля ═══
        self.wheat_fields = [
            pygame.Rect(100, 100, 250, 250),
            pygame.Rect(900, 100, 300, 250),
            pygame.Rect(100, 900, 300, 300),
            pygame.Rect(1400, 600, 350, 300),
            pygame.Rect(1400, 1000, 400, 350),
        ]

    def _generate_decorations(self):
        random.seed(888)

        # Деревья по краям
        tree_spots = [
            (30, 50), (1900, 80), (1850, 1400), (50, 1350),
            (1700, 200), (1750, 500), (80, 800), (1600, 1200),
            (300, 1400), (1000, 1500), (1500, 50), (1900, 900),
        ]
        for tx, ty in tree_spots:
            self.decorations.append({
                "type": "tree", "x": tx, "y": ty,
                "size": random.randint(50, 70),
                "color": random.choice([(45, 85, 42), (55, 95, 50), (38, 75, 38)])
            })
            self.colliders.append(pygame.Rect(tx + 18, ty + 45, 20, 20))

        # Цветы
        for _ in range(100):
            fx = random.randint(30, self.width - 30)
            fy = random.randint(30, self.height - 30)
            on_road = any(r.collidepoint(fx, fy) for r in self.roads)
            if not on_road:
                self.decorations.append({
                    "type": "flower", "x": fx, "y": fy,
                    "color": random.choice([
                        (255, 200, 80), (255, 100, 100), (200, 100, 255),
                        (255, 255, 100), (255, 150, 200), (150, 200, 255),
                        (255, 220, 150),
                    ])
                })

        # Камни
        for _ in range(20):
            rx = random.randint(50, self.width - 50)
            ry = random.randint(50, self.height - 50)
            self.decorations.append({
                "type": "rock", "x": rx, "y": ry,
                "size": random.randint(10, 25)
            })

        # Бабочки (визуальный эффект)
        self.butterflies = []
        for _ in range(15):
            bx = random.randint(100, self.width - 100)
            by = random.randint(100, self.height - 100)
            self.butterflies.append({
                "x": float(bx), "y": float(by),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(20, 60),
                "color": random.choice([
                    (255, 255, 100), (255, 200, 80), (200, 150, 255),
                    (255, 150, 150), (150, 255, 200),
                ]),
            })

    def _generate_ground(self):
        self.ground = pygame.Surface((self.width, self.height))

        # Базовая трава — светлее чем в городе
        base = (65, 110, 50)
        self.ground.fill(base)

        random.seed(999)

        # Вариации
        for _ in range(5000):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            v = random.randint(-10, 10)
            c = tuple(max(0, min(255, base[i] + v)) for i in range(3))
            pygame.draw.circle(self.ground, c, (x, y), random.randint(2, 6))

        # Пшеничные поля
        for field in self.wheat_fields:
            wheat_color = (190, 170, 80)
            pygame.draw.rect(self.ground, wheat_color, field)
            # Текстура пшеницы
            for _ in range(field.width * field.height // 20):
                wx = random.randint(field.x, field.x + field.width - 1)
                wy = random.randint(field.y, field.y + field.height - 1)
                wv = random.randint(-15, 15)
                wc = tuple(max(0, min(255, wheat_color[i] + wv)) for i in range(3))
                pygame.draw.line(self.ground, wc, (wx, wy), (wx, wy - random.randint(3, 8)), 1)
            # Рамка поля
            pygame.draw.rect(self.ground, (150, 130, 60), field, width=2)

        # Дороги
        road_color = (120, 100, 75)
        for road in self.roads:
            pygame.draw.rect(self.ground, road_color, road)
            for _ in range(road.width * road.height // 30):
                rx = random.randint(road.x, road.x + road.width - 1)
                ry = random.randint(road.y, road.y + road.height - 1)
                v = random.randint(-8, 8)
                c = tuple(max(0, min(255, road_color[i] + v)) for i in range(3))
                self.ground.set_at((rx, ry), c)

        # Забор на землю
        fence_color = (100, 80, 55)
        for f in self.fences:
            pygame.draw.rect(self.ground, fence_color, f)

    # ── Обновление ────────────────────────────────────────────────────

    def update(self, player_rect, dt):
        # Анимация бабочек
        for b in self.butterflies:
            b["phase"] += dt * 2
            b["x"] += math.sin(b["phase"]) * b["speed"] * dt
            b["y"] += math.cos(b["phase"] * 0.7) * b["speed"] * 0.5 * dt
            # Возврат в пределы карты
            b["x"] = max(50, min(self.width - 50, b["x"]))
            b["y"] = max(50, min(self.height - 50, b["y"]))

    def get_hovered_building(self):
        return None

    def get_hovered_npc(self):
        return None

    # ── Отрисовка ────────────────────────────────────────────────────

    def draw(self, surface, camera_x, camera_y, screen_w, screen_h):
        surface.blit(self.ground, (-camera_x, -camera_y))

        drawables = []
        for d in self.decorations:
            drawables.append((d["y"], "deco", d))
        for hs in self.haystacks:
            drawables.append((hs["y"] + 20, "hay", hs))

        # Мельница
        drawables.append((self.mill_y + 130, "mill", None))
        # Дом
        drawables.append((self.farmhouse["y"] + self.farmhouse["h"], "farmhouse", None))
        # Амбар
        drawables.append((self.barn["y"] + self.barn["h"], "barn", None))
        # Колодец
        drawables.append((self.well["y"] + 40, "well", None))

        drawables.sort(key=lambda d: d[0])

        for _, kind, obj in drawables:
            if kind == "deco":
                self._draw_deco(surface, obj, camera_x, camera_y)
            elif kind == "hay":
                self._draw_haystack(surface, obj, camera_x, camera_y)
            elif kind == "mill":
                self._draw_mill(surface, camera_x, camera_y)
            elif kind == "farmhouse":
                self._draw_farmhouse(surface, camera_x, camera_y)
            elif kind == "barn":
                self._draw_barn(surface, camera_x, camera_y)
            elif kind == "well":
                self._draw_well(surface, camera_x, camera_y)

        # Заборы 3D
        self._draw_fences(surface, camera_x, camera_y)

        # Бабочки
        self._draw_butterflies(surface, camera_x, camera_y)

    def _draw_deco(self, surface, d, cx, cy):
        sx = d["x"] - cx
        sy = d["y"] - cy

        if d["type"] == "tree":
            size = d["size"]
            color = d["color"]
            shadow = pygame.Surface((size, size // 3), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 35), (0, 0, size, size // 3))
            surface.blit(shadow, (sx, sy + size - 5))
            tw = size // 5
            pygame.draw.rect(surface, (80, 55, 35),
                             (sx + size // 2 - tw // 2, sy + size // 2, tw, size // 2))
            pygame.draw.circle(surface, color, (sx + size // 2, sy + size // 3), size // 2)
            lighter = tuple(min(255, c + 20) for c in color)
            pygame.draw.circle(surface, lighter, (sx + size // 2 - 5, sy + size // 4), size // 3)

        elif d["type"] == "rock":
            s = d["size"]
            pygame.draw.ellipse(surface, (110, 105, 100), (sx, sy, s, s * 2 // 3))
            pygame.draw.ellipse(surface, (85, 80, 75), (sx, sy, s, s * 2 // 3), width=1)

        elif d["type"] == "flower":
            pygame.draw.line(surface, (55, 110, 45), (sx, sy), (sx, sy + 8), 2)
            pygame.draw.circle(surface, d["color"], (sx, sy), 4)
            pygame.draw.circle(surface, (255, 255, 220), (sx, sy), 2)

    def _draw_haystack(self, surface, hs, cx, cy):
        sx = int(hs["x"] - cx)
        sy = int(hs["y"] - cy)
        s = hs["size"]
        # Тень
        shadow = pygame.Surface((s + 10, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 35), (0, 0, s + 10, 12))
        surface.blit(shadow, (sx - 5, sy + s - 8))
        # Сено
        pygame.draw.ellipse(surface, (200, 180, 100), (sx, sy, s, s))
        pygame.draw.ellipse(surface, (180, 160, 80), (sx, sy, s, s), width=2)
        # Верхушка
        pygame.draw.ellipse(surface, (220, 200, 120), (sx + 5, sy - 5, s - 10, s // 2))

    def _draw_mill(self, surface, cx, cy):
        mx = int(self.mill_x - cx)
        my = int(self.mill_y - cy)
        # Тень
        shadow = pygame.Surface((110, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 40), (0, 0, 110, 20))
        surface.blit(shadow, (mx, my + 120))
        # Корпус
        pygame.draw.rect(surface, (140, 120, 100), (mx + 20, my + 50, 60, 80))
        pygame.draw.rect(surface, (120, 100, 80), (mx + 20, my + 50, 60, 80), width=2)
        # Крыша
        pygame.draw.polygon(surface, (100, 70, 50),
                          [(mx + 10, my + 55), (mx + 50, my + 20), (mx + 90, my + 55)])
        # Дверь
        pygame.draw.rect(surface, (70, 50, 35), (mx + 40, my + 95, 20, 35), border_radius=2)
        # Лопасти
        t = pygame.time.get_ticks() / 1500
        lcx, lcy = mx + 50, my + 45
        for i in range(4):
            angle = t + i * math.pi / 2
            ex = lcx + int(40 * math.cos(angle))
            ey = lcy + int(40 * math.sin(angle))
            pygame.draw.line(surface, (130, 115, 95), (lcx, lcy), (ex, ey), 4)
            # Лопатка
            perp_angle = angle + math.pi / 2
            px = int(8 * math.cos(perp_angle))
            py = int(8 * math.sin(perp_angle))
            pygame.draw.line(surface, (150, 135, 115),
                           (ex - px, ey - py), (ex + px, ey + py), 2)
        # Ось
        pygame.draw.circle(surface, (100, 85, 70), (lcx, lcy), 5)

    def _draw_farmhouse(self, surface, cx, cy):
        fh = self.farmhouse
        fx = int(fh["x"] - cx)
        fy = int(fh["y"] - cy)
        # Стены
        pygame.draw.rect(surface, (120, 100, 80), (fx, fy + 30, fh["w"], fh["h"] - 30))
        pygame.draw.rect(surface, (100, 80, 60), (fx, fy + 30, fh["w"], fh["h"] - 30), width=2)
        # Крыша
        pygame.draw.polygon(surface, (140, 80, 60),
                          [(fx - 10, fy + 35), (fx + fh["w"] // 2, fy), (fx + fh["w"] + 10, fy + 35)])
        # Дверь
        pygame.draw.rect(surface, (65, 45, 30), (fx + 40, fy + 50, 25, 40), border_radius=2)
        pygame.draw.circle(surface, (180, 150, 50), (fx + 60, fy + 70), 3)
        # Окно
        pygame.draw.rect(surface, (180, 200, 220), (fx + 15, fy + 50, 18, 18))
        pygame.draw.rect(surface, (60, 45, 35), (fx + 15, fy + 50, 18, 18), width=2)

    def _draw_barn(self, surface, cx, cy):
        b = self.barn
        bx = int(b["x"] - cx)
        by = int(b["y"] - cy)
        # Стены
        pygame.draw.rect(surface, (130, 65, 55), (bx, by + 35, b["w"], b["h"] - 35))
        pygame.draw.rect(surface, (110, 50, 40), (bx, by + 35, b["w"], b["h"] - 35), width=2)
        # Крыша
        pygame.draw.polygon(surface, (100, 70, 55),
                          [(bx - 10, by + 40), (bx + b["w"] // 2, by), (bx + b["w"] + 10, by + 40)])
        # Ворота
        pygame.draw.rect(surface, (90, 45, 35), (bx + 35, by + 50, 50, 50), border_radius=3)
        # X на воротах
        pygame.draw.line(surface, (70, 35, 25), (bx + 40, by + 55), (bx + 80, by + 95), 3)
        pygame.draw.line(surface, (70, 35, 25), (bx + 80, by + 55), (bx + 40, by + 95), 3)

    def _draw_well(self, surface, cx, cy):
        w = self.well
        wx = int(w["x"] - cx)
        wy = int(w["y"] - cy)
        # Основание
        pygame.draw.ellipse(surface, (115, 105, 100), (wx, wy + 15, 40, 25))
        pygame.draw.rect(surface, (90, 80, 75), (wx + 5, wy, 30, 25))
        # Крыша
        pygame.draw.rect(surface, (80, 65, 50), (wx + 2, wy - 15, 36, 8))
        # Стойки
        pygame.draw.line(surface, (70, 55, 45), (wx + 8, wy - 15), (wx + 8, wy + 5), 3)
        pygame.draw.line(surface, (70, 55, 45), (wx + 32, wy - 15), (wx + 32, wy + 5), 3)
        # Вода
        pygame.draw.ellipse(surface, (80, 120, 170), (wx + 8, wy + 5, 24, 14))

    def _draw_fences(self, surface, cx, cy):
        for f in self.fences:
            fx = int(f.x - cx)
            fy = int(f.y - cy)
            if f.width > f.height:
                # Горизонтальный забор
                for post_x in range(fx, fx + f.width, 25):
                    pygame.draw.rect(surface, (90, 70, 50),
                                   (post_x, fy - 15, 5, 20))
                pygame.draw.line(surface, (110, 90, 65),
                               (fx, fy - 10), (fx + f.width, fy - 10), 3)
                pygame.draw.line(surface, (110, 90, 65),
                               (fx, fy - 3), (fx + f.width, fy - 3), 3)
            else:
                # Вертикальный забор
                for post_y in range(fy, fy + f.height, 25):
                    pygame.draw.rect(surface, (90, 70, 50),
                                   (fx - 2, post_y, 8, 5))
                pygame.draw.line(surface, (110, 90, 65),
                               (fx, fy), (fx, fy + f.height), 3)
                pygame.draw.line(surface, (110, 90, 65),
                               (fx + 4, fy), (fx + 4, fy + f.height), 3)

    def _draw_butterflies(self, surface, cx, cy):
        for b in self.butterflies:
            bx = int(b["x"] - cx)
            by = int(b["y"] - cy)
            wing_phase = math.sin(pygame.time.get_ticks() / 100 + b["phase"])
            wing_w = int(4 + abs(wing_phase) * 4)
            # Крылья
            pygame.draw.ellipse(surface, b["color"],
                              (bx - wing_w, by - 2, wing_w, 5))
            pygame.draw.ellipse(surface, b["color"],
                              (bx + 1, by - 2, wing_w, 5))
            # Тело
            pygame.draw.line(surface, (40, 30, 20), (bx, by - 1), (bx, by + 3), 1)