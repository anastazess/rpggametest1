import pygame
import random
from game.constants import *
from game.world.buildings import (Building, GuildBuilding, ShopBuilding,
                                   TavernBuilding, BlacksmithBuilding,
                                   TempleBuilding)
from game.world.npc import (NPC, create_guard, create_villager,
                            create_old_man, NPCAppearance)


# ── Безопасная точка спавна (свободная от коллайдеров) ──────────────
PLAYER_SPAWN_X = 450
PLAYER_SPAWN_Y = 680   # На дороге, подальше от патрульного


class WanderingNPC(NPC):
    """NPC который случайно гуляет по заданной зоне."""

    def __init__(self, x, y, name, appearance, dialogues,
                 zone_x, zone_y, zone_w, zone_h,
                 wander_speed=35, wait_range=(2.0, 5.0)):
        super().__init__(x, y, name, appearance, dialogues, "wanderer")

        self.zone = pygame.Rect(zone_x, zone_y, zone_w, zone_h)
        self.speed = wander_speed

        self.target_x = float(x)
        self.target_y = float(y)

        self.wait_timer  = 0.0           # сколько стоим
        self.move_timer  = 0.0           # сколько идём
        self.wait_range  = wait_range
        self.state = "waiting"           # waiting | moving

        self._pick_new_target()

    def _pick_new_target(self):
        """Выбираем случайную точку внутри зоны."""
        margin = 30
        self.target_x = float(random.randint(
            self.zone.x + margin,
            self.zone.x + self.zone.width  - margin
        ))
        self.target_y = float(random.randint(
            self.zone.y + margin,
            self.zone.y + self.zone.height - margin
        ))
        self.move_timer = random.uniform(3.0, 7.0)

    def update(self, dt: float, player_rect: pygame.Rect):
        self.anim_time += dt

        # Проверка близости игрока
        import math
        px = player_rect.centerx
        py = player_rect.centery
        cx = self.x + self.width  // 2
        cy = self.y + self.height // 2
        dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
        self.hovered = dist < self.interaction_radius

        # Если игрок рядом — стоим и смотрим на него
        if self.hovered:
            self.moving = False
            self.state  = "waiting"
            dx = px - cx
            dy = py - cy
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down"  if dy > 0 else "up"
            return

        if self.state == "waiting":
            self.wait_timer -= dt
            self.moving = False
            if self.wait_timer <= 0:
                self._pick_new_target()
                self.state = "moving"

        elif self.state == "moving":
            self.move_timer -= dt

            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist_to_target = math.sqrt(dx * dx + dy * dy)

            if dist_to_target < 8 or self.move_timer <= 0:
                # Дошли или время вышло — ждём
                self.state      = "waiting"
                self.wait_timer = random.uniform(*self.wait_range)
                self.moving     = False
            else:
                self.moving = True
                nx = dx / dist_to_target
                ny = dy / dist_to_target
                self.x += nx * self.speed * dt
                self.y += ny * self.speed * dt

                # Не выходим за зону
                self.x = max(float(self.zone.x + 10),
                             min(self.x, float(self.zone.x + self.zone.width  - 10)))
                self.y = max(float(self.zone.y + 10),
                             min(self.y, float(self.zone.y + self.zone.height - 10)))

                # Направление
                if abs(dx) > abs(dy):
                    self.direction = "right" if dx > 0 else "left"
                else:
                    self.direction = "down"  if dy > 0 else "up"


def make_wanderer(x, y, name, role,
                  zone_x, zone_y, zone_w, zone_h,
                  outfit=(90, 75, 65),
                  hair=None,
                  skin=None,
                  has_beard=False,
                  has_hat=False,
                  hair_style="short",
                  accessory="",
                  dialogues=None,
                  speed=35):
    """Фабрика для гуляющего NPC."""
    appearance = NPCAppearance(
        body_color   = outfit,
        skin_color   = skin  or (
            random.randint(200, 240),
            random.randint(165, 205),
            random.randint(145, 185)
        ),
        hair_color   = hair or (
            random.randint(30, 120),
            random.randint(20,  80),
            random.randint(10,  50)
        ),
        hair_style   = hair_style,
        outfit_color = outfit,
        has_beard    = has_beard,
        has_hat      = has_hat,
        hat_color    = tuple(max(0, c - 20) for c in outfit),
        accessory    = accessory,
    )

    default_dialogues = [
        {"speaker": name,
         "role": role,
         "text": random.choice([
             "Добрый день, путник!",
             "Чудесная погода сегодня.",
             "В таверне опять шумят...",
             "Осторожнее в переулках.",
             "Слышали? В лесу снова видели монстров.",
             "Гильдия набирает новых искателей!",
             "Кузнец говорит, что скоро поднимет цены.",
             "Не забудьте заплатить налоги старосте.",
         ]),
         "portrait_color": (150, 130, 120)},
    ]

    npc = WanderingNPC(
        x, y, name, appearance,
        dialogues or default_dialogues,
        zone_x, zone_y, zone_w, zone_h,
        wander_speed=speed,
    )
    npc.role = role
    return npc


class GameMap:
    """Расширенная игровая карта города."""

    def __init__(self, width=1800, height=1400):
        self.width  = width
        self.height = height

        self.colliders   = []
        self.decorations = []

        # Дороги
        self.roads = [
            pygame.Rect(0,    500, self.width, 100),   # главная горизонт.
            pygame.Rect(400,  0,   100, self.height),  # главная вертикал.
            pygame.Rect(1000, 200, 80,  900),           # вторая вертикал.
            pygame.Rect(400,  900, 700, 80),            # поперечная
            pygame.Rect(350,  450, 200, 200),           # площадь
        ]

        # Границы карты
        self.colliders.extend([
            pygame.Rect(-50,        0,          50,         self.height),
            pygame.Rect(self.width, 0,          50,         self.height),
            pygame.Rect(0,          -50,        self.width, 50),
            pygame.Rect(0,          self.height, self.width, 50),
        ])

        # Здания
        self.buildings = [
            GuildBuilding(200, 180),
            ShopBuilding(550, 220),
            TavernBuilding(750, 250),
            BlacksmithBuilding(200, 700),

            # Храм богини — добавляем сюда
            TempleBuilding(900, 700),  # <-- НОВОЕ

            Building(550, 700, 100, 90, "Жилой дом", (85, 75, 70), (90, 60, 55)),
            Building(700, 720, 90, 85, "Жилой дом", (80, 70, 65), (85, 55, 50)),
            Building(1150, 300, 110, 95, "Склад", (70, 65, 60), (75, 50, 45)),
            Building(1150, 500, 100, 90, "Лавка травника", (65, 85, 65), (55, 75, 55)),
            Building(1150, 750, 120, 100, "Казармы", (75, 70, 80), (65, 55, 70)),
            Building(550, 1050, 130, 100, "Часовня", (90, 85, 95), (100, 90, 110)),
            Building(150, 1050, 100, 90, "Дом старосты", (95, 80, 70), (105, 70, 60)),
        ]

        for b in self.buildings:
            self.colliders.append(b.collision_rect)

        # NPC
        self.street_npcs = []
        self._spawn_street_npcs()

        # Декорации
        self._generate_decorations()

        # Земля
        self._generate_ground_texture()

    # ── Спавн NPC ────────────────────────────────────────────────────

    def _spawn_street_npcs(self):

        # ── Стражники (статичные) ─────────────────────────────────────
        g1 = create_guard()
        g1.x, g1.y = 50, 520
        g1.name = "Стражник западных ворот"
        self.street_npcs.append(g1)

        g2 = create_guard()
        g2.x, g2.y = 1700, 520
        g2.name = "Стражник восточных ворот"
        self.street_npcs.append(g2)

        # ── Патрульный стражник ───────────────────────────────────────
        # Маршрут ВДАЛИ от точки спавна игрока (450, 680)
        patrol = create_guard()
        patrol.x, patrol.y = 800, 510
        patrol.name = "Патрульный"
        patrol.patrol_points = [
            (800, 510),
            (1050, 510),
            (1050, 560),
            (800, 560),
        ]
        self.street_npcs.append(patrol)

        # ── Второй патрульный (у казарм) ─────────────────────────────
        patrol2 = create_guard()
        patrol2.x, patrol2.y = 1150, 660
        patrol2.name = "Казарменный стражник"
        patrol2.patrol_points = [
            (1150, 660),
            (1300, 660),
            (1300, 730),
            (1150, 730),
        ]
        self.street_npcs.append(patrol2)

        # ── Мудрец (статичный, у часовни) ────────────────────────────
        sage = create_old_man()
        sage.x, sage.y = 620, 1060
        self.street_npcs.append(sage)

        # ── Гуляющие NPC — ЗОНА: главная площадь и дороги ───────────

        # Торговка с корзиной
        self.street_npcs.append(make_wanderer(
            480, 520, "Торговка Марта", "торговка",
            zone_x=360, zone_y=460, zone_w=180, zone_h=180,
            outfit=(100, 80, 70), hair_style="long",
            dialogues=[
                {"speaker": "Марта", "role": "Торговка на площади",
                 "text": "Свежие яблоки! Покупайте свежие яблоки!",
                 "portrait_color": (180, 140, 110)},
                {"speaker": "Марта", "role": "Торговка на площади",
                 "text": "Три яблока за медяк — лучшая цена в городе!",
                 "portrait_color": (180, 140, 110)},
            ],
        ))

        # Фермер
        self.street_npcs.append(make_wanderer(
            430, 560, "Фермер Том", "фермер",
            zone_x=405, zone_y=510, zone_w=150, zone_h=150,
            outfit=(80, 95, 70), hair_style="short",
            has_hat=True, speed=28,
            dialogues=[
                {"speaker": "Том", "role": "Фермер",
                 "text": "Урожай в этом году неплохой, если волки не сожрут.",
                 "portrait_color": (160, 130, 100)},
            ],
        ))

        # Горожанин-пьяница (у таверны)
        self.street_npcs.append(make_wanderer(
            780, 490, "Пьяница Якоб", "житель",
            zone_x=700, zone_y=440, zone_w=200, zone_h=140,
            outfit=(70, 60, 55), hair_style="bald",
            has_beard=True, speed=20,
            dialogues=[
                {"speaker": "Якоб", "role": "Завсегдатай таверны",
                 "text": "Ик... ещё один стаканчик не помешает...",
                 "portrait_color": (140, 110, 90)},
                {"speaker": "Якоб", "role": "Завсегдатай таверны",
                 "text": "Я те говорю... дракон! Настоящий! Вот этими глазами видел.",
                 "portrait_color": (140, 110, 90)},
            ],
        ))

        # Ребёнок (бегает быстро)
        self.street_npcs.append(make_wanderer(
            500, 540, "Мальчишка Пит", "ребёнок",
            zone_x=360, zone_y=460, zone_w=250, zone_h=200,
            outfit=(90, 110, 140), hair_style="short",
            speed=80,
            dialogues=[
                {"speaker": "Пит", "role": "Мальчишка",
                 "text": "Ты искатель?! Покажи свой меч!",
                 "portrait_color": (200, 170, 140)},
                {"speaker": "Пит", "role": "Мальчишка",
                 "text": "Когда вырасту — стану самым крутым искателем!",
                 "portrait_color": (200, 170, 140)},
            ],
        ))

        # Монах у часовни
        self.street_npcs.append(make_wanderer(
            600, 1080, "Монах Эриус", "монах",
            zone_x=540, zone_y=1020, zone_w=160, zone_h=120,
            outfit=(120, 115, 130), hair_style="bald",
            accessory="hood", speed=22,
            dialogues=[
                {"speaker": "Эриус", "role": "Монах храма Авэлин",
                 "text": "Свет Создателя да пребудет с тобой, путник.",
                 "portrait_color": (170, 160, 190)},
                {"speaker": "Эриус", "role": "Монах храма Авэлин",
                 "text": "Часовня открыта для всех. Зайди, обрети покой.",
                 "portrait_color": (170, 160, 190)},
            ],
        ))

        # Старушка у дома старосты
        self.street_npcs.append(make_wanderer(
            185, 1060, "Бабушка Хельга", "пожилая жительница",
            zone_x=130, zone_y=1020, zone_w=160, zone_h=120,
            outfit=(110, 100, 115), hair_style="long",
            has_beard=False, speed=18,
            dialogues=[
                {"speaker": "Хельга", "role": "Пожилая жительница",
                 "text": "В мои годы уже и ноги не те... А ты куда спешишь?",
                 "portrait_color": (190, 165, 150)},
                {"speaker": "Хельга", "role": "Пожилая жительница",
                 "text": "Осторожней, молодой. Я помню, как этот город был другим.",
                 "portrait_color": (190, 165, 150)},
            ],
        ))

        # Рыбак (у нижней части карты)
        self.street_npcs.append(make_wanderer(
            700, 1200, "Рыбак Олег", "рыбак",
            zone_x=600, zone_y=1150, zone_w=200, zone_h=150,
            outfit=(65, 80, 90), hair_style="short",
            has_beard=True, speed=25,
            dialogues=[
                {"speaker": "Олег", "role": "Рыбак",
                 "text": "Хорошая рыбалка сегодня. Хочешь купить рыбку?",
                 "portrait_color": (130, 150, 160)},
            ],
        ))

        # Подмастерье кузнеца (гуляет между кузницей и казармами)
        self.street_npcs.append(make_wanderer(
            900, 700, "Подмастерье Эрик", "подмастерье",
            zone_x=200, zone_y=650, zone_w=980, zone_h=120,
            outfit=(60, 55, 55), hair_style="short",
            accessory="apron", speed=45,
            dialogues=[
                {"speaker": "Эрик", "role": "Подмастерье кузнеца",
                 "text": "Горан послал за углём. Некогда болтать!",
                 "portrait_color": (150, 120, 100)},
            ],
        ))

        # Дворянин с тростью
        self.street_npcs.append(make_wanderer(
            450, 500, "Дворянин Лерой", "дворянин",
            zone_x=360, zone_y=455, zone_w=300, zone_h=120,
            outfit=(110, 95, 130), hair_style="ponytail",
            has_hat=True, speed=30,
            dialogues=[
                {"speaker": "Лерой", "role": "Дворянин",
                 "text": "Позвольте! Вы задели мой плащ, невежа.",
                 "portrait_color": (160, 140, 190)},
                {"speaker": "Лерой", "role": "Дворянин",
                 "text": "Я пожалуюсь старосте на состояние этих мостовых!",
                 "portrait_color": (160, 140, 190)},
            ],
        ))

        # Учёный / алхимик (у лавки травника)
        self.street_npcs.append(make_wanderer(
            1170, 490, "Алхимик Сол", "алхимик",
            zone_x=1080, zone_y=450, zone_w=180, zone_h=120,
            outfit=(70, 90, 80), hair_style="long",
            has_beard=True, accessory="hood", speed=20,
            dialogues=[
                {"speaker": "Сол", "role": "Алхимик",
                 "text": "Не трогай те зелья! Они нестабильны.",
                 "portrait_color": (120, 160, 140)},
                {"speaker": "Сол", "role": "Алхимик",
                 "text": "Мне нужны синие грибы из Туманного леса. Принесёшь — хорошо заплачу.",
                 "portrait_color": (120, 160, 140)},
            ],
        ))

        signpost_guard = create_guard()
        signpost_guard.x, signpost_guard.y = 1720, 560
        signpost_guard.name = "Стражник у выхода"
        signpost_guard.dialogues = [
            {"speaker": "Стражник",
             "role": "Городская стража Валенхольма",
             "text": "За воротами — поля Валенхольма. Дальше — Туманный лес. Будь осторожен.",
             "portrait_color": (120, 120, 140)},
        ]
        self.street_npcs.append(signpost_guard)

        # Странник (приезжий)
        self.street_npcs.append(make_wanderer(
            550, 550, "Странник с севера", "странник",
            zone_x=420, zone_y=500, zone_w=350, zone_h=120,
            outfit=(85, 80, 100), hair_style="long",
            speed=38,
            dialogues=[
                {"speaker": "Странник", "role": "Путешественник с севера",
                 "text": "Я пришёл из Северных пределов. Дорога была нелёгкой.",
                 "portrait_color": (150, 145, 170)},
                {"speaker": "Странник", "role": "Путешественник с севера",
                 "text": "На севере тоже неспокойно. Тьма наступает отовсюду.",
                 "portrait_color": (150, 145, 170)},
            ],
        ))


    # ── Декорации ────────────────────────────────────────────────────

    def _generate_decorations(self):
        random.seed(42)

        tree_clusters = [
            [(30, 100), (80, 160), (30, 260), (120, 320)],
            [(1600, 150), (1700, 280), (1650, 400), (1550, 320)],
            [(100, 1200), (200, 1280), (350, 1200), (280, 1340)],
            [(1400, 1100), (1500, 1200), (1600, 1160), (1560, 1300)],
            [(620, 640), (680, 670), (750, 630)],
            [(900, 340), (950, 370), (880, 410)],
            [(50, 700), (120, 760), (60, 820)],
            [(1700, 700), (1750, 780), (1680, 850)],
        ]

        for cluster in tree_clusters:
            for tx, ty in cluster:
                jx = tx + random.randint(-20, 20)
                jy = ty + random.randint(-20, 20)
                self.decorations.append({
                    "type": "tree", "x": jx, "y": jy,
                    "size":  random.randint(45, 65),
                    "color": random.choice([
                        (40, 80, 40), (50, 90, 45),
                        (35, 70, 35), (45, 85, 50),
                    ])
                })
                self.colliders.append(
                    pygame.Rect(jx + 15, jy + 40, 20, 20))

        for _ in range(30):
            rx = random.randint(50, self.width  - 50)
            ry = random.randint(50, self.height - 50)
            if not any(r.collidepoint(rx, ry) for r in self.roads):
                self.decorations.append({
                    "type": "rock", "x": rx, "y": ry,
                    "size": random.randint(10, 30),
                })

        for _ in range(80):
            fx = random.randint(30, self.width  - 30)
            fy = random.randint(30, self.height - 30)
            if not any(r.collidepoint(fx, fy) for r in self.roads):
                self.decorations.append({
                    "type": "flower", "x": fx, "y": fy,
                    "color": random.choice([
                        (255, 100, 100), (255, 200, 100),
                        (200, 100, 255), (255, 255, 100),
                        (255, 150, 200), (150, 200, 255),
                    ])
                })

        # Фонтан
        self.decorations.append({"type": "fountain", "x": 420, "y": 510, "size": 60})
        self.colliders.append(pygame.Rect(420, 510, 60, 60))

        # Колодцы
        for wx, wy in [(750, 850), (1100, 450)]:
            self.decorations.append({"type": "well", "x": wx, "y": wy, "size": 40})
            self.colliders.append(pygame.Rect(wx, wy, 40, 40))

        # Скамейки
        for bx, by in [(500, 610), (380, 515), (540, 475)]:
            self.decorations.append({"type": "bench", "x": bx, "y": by})

    # ── Земля ────────────────────────────────────────────────────────

    def _generate_ground_texture(self):
        self.ground = pygame.Surface((self.width, self.height))
        base = (50, 85, 40)
        self.ground.fill(base)

        random.seed(123)
        for _ in range(4000):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            v = random.randint(-12, 12)
            c = tuple(max(0, min(255, base[i] + v)) for i in range(3))
            pygame.draw.circle(self.ground, c, (x, y), random.randint(2, 5))

        road_color = (95, 80, 65)
        for road in self.roads:
            pygame.draw.rect(self.ground, road_color, road)
            for _ in range(road.width * road.height // 40):
                rx = random.randint(road.x, road.x + road.width  - 1)
                ry = random.randint(road.y, road.y + road.height - 1)
                v  = random.randint(-8, 8)
                c  = tuple(max(0, min(255, road_color[i] + v)) for i in range(3))
                self.ground.set_at((rx, ry), c)

        # Площадь — плитка
        plaza = self.roads[4]
        ts = 30
        for tx in range(plaza.x, plaza.x + plaza.width, ts):
            for ty in range(plaza.y, plaza.y + plaza.height, ts):
                col = (85, 75, 65) if (tx // ts + ty // ts) % 2 == 0 \
                      else (75, 65, 55)
                pygame.draw.rect(self.ground, col, (tx, ty, ts - 1, ts - 1))

    # ── Update / Draw ─────────────────────────────────────────────────

    def update(self, player_rect: pygame.Rect, dt: float):
        for b   in self.buildings:
            b.update(player_rect)
        for npc in self.street_npcs:
            npc.update(dt, player_rect)

    def get_hovered_building(self):
        for b in self.buildings:
            if b.hovered:
                return b
        return None

    def get_hovered_npc(self):
        for npc in self.street_npcs:
            if npc.hovered:
                return npc
        return None

    def draw(self, surface, camera_x, camera_y, screen_w, screen_h):
        surface.blit(self.ground, (-camera_x, -camera_y))

        drawables = []
        for deco in self.decorations:
            drawables.append((deco["y"], "deco", deco))
        for b in self.buildings:
            drawables.append((b.y + b.height, "building", b))
        for npc in self.street_npcs:
            drawables.append((npc.y + npc.height, "npc", npc))
        drawables.sort(key=lambda d: d[0])

        for _, kind, obj in drawables:
            if kind == "deco":
                self._draw_decoration(surface, obj, camera_x, camera_y)
            elif kind == "building":
                obj.draw(surface, camera_x, camera_y)
            elif kind == "npc":
                obj.draw(surface, camera_x, camera_y)

    def _draw_decoration(self, surface, deco, camera_x, camera_y):
        sx = deco["x"] - camera_x
        sy = deco["y"] - camera_y

        if deco["type"] == "tree":
            size  = deco["size"]
            color = deco["color"]
            shadow = pygame.Surface((size, size // 3), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 40), (0, 0, size, size // 3))
            surface.blit(shadow, (sx, sy + size - 5))
            tw = size // 5
            th = size // 2
            pygame.draw.rect(surface, (70, 50, 30),
                             (sx + size // 2 - tw // 2,
                              sy + size - th, tw, th))
            pygame.draw.circle(surface, color,
                               (sx + size // 2, sy + size // 3), size // 2)
            pygame.draw.circle(surface, color,
                               (sx + size // 3, sy + size // 2), size // 3)
            pygame.draw.circle(surface, color,
                               (sx + size * 2 // 3, sy + size // 2), size // 3)

        elif deco["type"] == "rock":
            size = deco["size"]
            pygame.draw.ellipse(surface, (100, 95, 90),
                                (sx, sy, size, size * 2 // 3))
            pygame.draw.ellipse(surface, (80, 75, 70),
                                (sx, sy, size, size * 2 // 3), width=1)

        elif deco["type"] == "flower":
            pygame.draw.line(surface, (50, 100, 40),
                             (sx, sy), (sx, sy + 8), 2)
            pygame.draw.circle(surface, deco["color"], (sx, sy), 4)
            pygame.draw.circle(surface, (255, 255, 200), (sx, sy), 2)

        elif deco["type"] == "fountain":
            size = deco["size"]
            pygame.draw.ellipse(surface, (120, 115, 110),
                                (sx, sy + size // 2, size, size // 2))
            pygame.draw.ellipse(surface, (90, 85, 80),
                                (sx, sy + size // 2, size, size // 2), width=2)
            pygame.draw.ellipse(surface, (80, 130, 180),
                                (sx + 8, sy + size // 2 + 5,
                                 size - 16, size // 3))
            pygame.draw.rect(surface, (140, 130, 125),
                             (sx + size // 2 - 5, sy + 10, 10, size // 2))
            pygame.draw.line(surface, (150, 200, 255),
                             (sx + size // 2, sy + 10),
                             (sx + size // 2 - 10, sy + size // 2 - 5), 2)
            pygame.draw.line(surface, (150, 200, 255),
                             (sx + size // 2, sy + 10),
                             (sx + size // 2 + 10, sy + size // 2 - 5), 2)

        elif deco["type"] == "well":
            size = deco["size"]
            pygame.draw.ellipse(surface, (110, 100, 95),
                                (sx, sy + size // 3, size, size // 2))
            pygame.draw.rect(surface, (80, 70, 65),
                             (sx + 5, sy, size - 10, size // 2))
            pygame.draw.line(surface, (60, 50, 45),
                             (sx + size // 2, sy - 10),
                             (sx + size // 2, sy + 5), 3)
            pygame.draw.rect(surface, (70, 55, 45),
                             (sx + 5, sy - 15, size - 10, 8))

        elif deco["type"] == "bench":
            pygame.draw.rect(surface, (100, 75, 55),
                             (sx, sy, 50, 15), border_radius=3)
            pygame.draw.rect(surface, (80, 60, 45),
                             (sx + 5, sy + 15, 8, 10))
            pygame.draw.rect(surface, (80, 60, 45),
                             (sx + 37, sy + 15, 8, 10))