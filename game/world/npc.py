import pygame
import math
import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from game.constants import *


@dataclass
class NPCAppearance:
    """Внешний вид NPC."""
    body_color: tuple = (80, 60, 140)
    skin_color: tuple = (230, 190, 160)
    hair_color: tuple = (60, 40, 30)
    hair_style: str = "short"  # short, long, bald, ponytail
    outfit_color: tuple = (100, 80, 60)
    has_beard: bool = False
    has_hat: bool = False
    hat_color: tuple = (80, 60, 50)
    accessory: str = ""  # apron, hood, cape


class NPC:
    """Базовый класс NPC."""

    def __init__(self, x: int, y: int, name: str,
                 appearance: NPCAppearance = None,
                 dialogues: List[dict] = None,
                 role: str = "villager"):
        self.x = x
        self.y = y
        self.name = name
        self.role = role
        self.appearance = appearance or NPCAppearance()
        self.dialogues = dialogues or []

        self.width = 32
        self.height = 48

        # Анимация
        self.anim_time = random.uniform(0, 10)
        self.idle_offset = random.uniform(0, math.pi * 2)
        self.direction = random.choice(["down", "left", "right"])

        # Взаимодействие
        self.hovered = False
        self.interaction_radius = 60

        # Движение (для патрулирующих NPC)
        self.patrol_points: List[tuple] = []
        self.patrol_index = 0
        self.moving = False
        self.speed = 40

        self.font = pygame.font.SysFont("segoeui", 12, bold=True)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def interaction_rect(self):
        return pygame.Rect(
            self.x - 15, self.y + self.height - 30,
            self.width + 30, 50
        )

    def update(self, dt: float, player_rect: pygame.Rect):
        self.anim_time += dt

        # Проверка близости игрока
        px = player_rect.centerx
        py = player_rect.centery
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
        self.hovered = dist < self.interaction_radius

        # Поворот к игроку если близко
        if self.hovered:
            dx = px - cx
            dy = py - cy
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

        # Патрулирование
        if self.patrol_points and not self.hovered:
            target = self.patrol_points[self.patrol_index]
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 5:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
                self.moving = False
            else:
                self.moving = True
                nx = dx / dist
                ny = dy / dist
                self.x += nx * self.speed * dt
                self.y += ny * self.speed * dt

                if abs(dx) > abs(dy):
                    self.direction = "right" if dx > 0 else "left"
                else:
                    self.direction = "down" if dy > 0 else "up"

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        # Idle анимация
        idle_bob = math.sin(self.anim_time * 2 + self.idle_offset) * 1.5
        if self.moving:
            idle_bob = math.sin(self.anim_time * 10) * 2

        a = self.appearance

        # Тень
        shadow = pygame.Surface((30, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), (0, 0, 30, 10))
        surface.blit(shadow, (sx + 1, sy + 42))

        # Тело
        body_y = sy + 18 + int(idle_bob)
        pygame.draw.rect(surface, a.outfit_color,
                         (sx + 4, body_y, 24, 28), border_radius=4)

        # Аксессуар - фартук
        if a.accessory == "apron":
            pygame.draw.rect(surface, (240, 230, 210),
                             (sx + 6, body_y + 8, 20, 18), border_radius=2)

        # Капюшон
        if a.accessory == "hood":
            pygame.draw.arc(surface, a.outfit_color,
                            (sx + 2, sy + 2, 28, 30), 0, math.pi, 5)

        # Голова
        head_x = sx + self.width // 2
        head_y = sy + 14 + int(idle_bob)
        pygame.draw.circle(surface, a.skin_color, (head_x, head_y), 10)

        # Волосы
        if a.hair_style == "short":
            pygame.draw.arc(surface, a.hair_color,
                            (head_x - 10, head_y - 12, 20, 16), 0, math.pi, 4)
        elif a.hair_style == "long":
            pygame.draw.arc(surface, a.hair_color,
                            (head_x - 10, head_y - 12, 20, 16), 0, math.pi, 4)
            pygame.draw.rect(surface, a.hair_color,
                             (head_x - 10, head_y - 2, 5, 20), border_radius=2)
            pygame.draw.rect(surface, a.hair_color,
                             (head_x + 5, head_y - 2, 5, 20), border_radius=2)
        elif a.hair_style == "ponytail":
            pygame.draw.arc(surface, a.hair_color,
                            (head_x - 10, head_y - 12, 20, 16), 0, math.pi, 4)
            pygame.draw.ellipse(surface, a.hair_color,
                                (head_x - 3, head_y - 18, 6, 10))
        elif a.hair_style == "bald":
            pass  # Нет волос

        # Борода
        if a.has_beard:
            pygame.draw.ellipse(surface, a.hair_color,
                                (head_x - 6, head_y + 4, 12, 10))

        # Шляпа
        if a.has_hat:
            pygame.draw.rect(surface, a.hat_color,
                             (head_x - 12, head_y - 14, 24, 6), border_radius=2)
            pygame.draw.rect(surface, a.hat_color,
                             (head_x - 7, head_y - 22, 14, 10), border_radius=3)

        # Глаза
        if self.direction != "up":
            eye_y = head_y
            if self.direction == "down":
                pygame.draw.circle(surface, (40, 30, 20), (head_x - 4, eye_y), 2)
                pygame.draw.circle(surface, (40, 30, 20), (head_x + 4, eye_y), 2)
            elif self.direction == "left":
                pygame.draw.circle(surface, (40, 30, 20), (head_x - 5, eye_y), 2)
            else:
                pygame.draw.circle(surface, (40, 30, 20), (head_x + 5, eye_y), 2)

        # Ноги
        leg_y = sy + 44 + int(idle_bob)
        if self.moving:
            offset = int(math.sin(self.anim_time * 12) * 3)
            pygame.draw.rect(surface, (50, 40, 35),
                             (sx + 9, leg_y - offset, 5, 5), border_radius=2)
            pygame.draw.rect(surface, (50, 40, 35),
                             (sx + 18, leg_y + offset, 5, 5), border_radius=2)
        else:
            pygame.draw.rect(surface, (50, 40, 35),
                             (sx + 9, leg_y, 5, 5), border_radius=2)
            pygame.draw.rect(surface, (50, 40, 35),
                             (sx + 18, leg_y, 5, 5), border_radius=2)

        # Имя и подсказка при наведении
        if self.hovered:
            self._draw_interaction_hint(surface, sx, sy)

    def _draw_interaction_hint(self, surface, sx, sy):
        # Рамка
        hint_rect = pygame.Rect(sx - 10, sy + self.height - 5,
                                self.width + 20, 25)
        hint_surf = pygame.Surface((hint_rect.width, hint_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(hint_surf, (*COLOR_ACCENT[:3], 40),
                         (0, 0, hint_rect.width, hint_rect.height), border_radius=6)
        pygame.draw.rect(hint_surf, (*COLOR_ACCENT[:3], 150),
                         (0, 0, hint_rect.width, hint_rect.height), width=1, border_radius=6)
        surface.blit(hint_surf, hint_rect.topleft)

        # Имя
        name_surf = self.font.render(self.name, True, COLOR_TEXT)
        name_x = sx + self.width // 2 - name_surf.get_width() // 2
        surface.blit(name_surf, (name_x, sy - 18))

        # Подсказка [E]
        hint = "[E] Говорить"
        hint_font = pygame.font.SysFont("segoeui", 11)
        hint_s = hint_font.render(hint, True, COLOR_ACCENT)
        hint_x = sx + self.width // 2 - hint_s.get_width() // 2
        surface.blit(hint_s, (hint_x, sy + self.height))

    def get_dialogues(self) -> List[dict]:
        """Возвращает диалоги с данными о внешности."""
        result = []
        for d in self.dialogues:
            entry = d.copy()
            entry["appearance"] = self.appearance
            result.append(entry)
        return result


# ===== Предустановленные NPC =====

def create_blacksmith() -> NPC:
    appearance = NPCAppearance(
        body_color=(60, 50, 50), skin_color=(200, 160, 130),
        hair_color=(40, 30, 25), hair_style="bald",
        outfit_color=(80, 60, 50), has_beard=True, accessory="apron"
    )
    dialogues = [
        {"speaker": "Горан",
         "role": "Мастер-кузнец Валенхольма",
         "text": "*Удар молота* Чего желаешь, путник?",
         "portrait_color": (150, 100, 80)},
        {"speaker": "Горан",
         "role": "Мастер-кузнец Валенхольма",
         "text": "Мои клинки — лучшие в Валенхольме. Спроси любого стражника.",
         "portrait_color": (150, 100, 80)},
        {"speaker": "Горан",
         "role": "Мастер-кузнец Валенхольма",
         "text": "Если принесёшь железной руды, выкую что-нибудь особенное.",
         "portrait_color": (150, 100, 80)},
    ]
    npc = NPC(0, 0, "Кузнец Горан", appearance, dialogues, "blacksmith")
    npc.appearance = appearance  # <-- ДОБАВИТЬ
    return npc


def create_merchant() -> NPC:
    appearance = NPCAppearance(
        body_color=(60, 90, 60), skin_color=(235, 200, 170),
        hair_color=(100, 70, 40), hair_style="short",
        outfit_color=(70, 100, 70), has_hat=True, hat_color=(60, 80, 60)
    )
    dialogues = [
        {"speaker": "Браен",
         "role": "Торговец снаряжением",
         "text": "Добро пожаловать! У меня есть всё для настоящего героя!",
         "portrait_color": (100, 180, 100)},
        {"speaker": "Браен",
         "role": "Торговец снаряжением",
         "text": "Зелья, свитки, снаряжение — по лучшим ценам!",
         "portrait_color": (100, 180, 100)},
        {"speaker": "Браен",
         "role": "Торговец снаряжением",
         "text": "Скидка для членов Гильдии — 10%!",
         "portrait_color": (100, 180, 100)},
    ]
    npc = NPC(0, 0, "Торговец Браен", appearance, dialogues, "merchant")
    npc.appearance = appearance  # <-- ДОБАВИТЬ
    return npc


def create_innkeeper() -> NPC:
    appearance = NPCAppearance(
        body_color=(100, 70, 50), skin_color=(220, 180, 150),
        hair_color=(80, 50, 30), hair_style="short",
        outfit_color=(120, 80, 50), has_beard=True,
    )
    dialogues = [
        {"speaker": "Олаф",
         "role": "Хозяин таверны «Пьяный Грифон»",
         "text": "Добро пожаловать в 'Пьяного Грифона'!",
         "portrait_color": (180, 120, 80)},
        {"speaker": "Олаф",
         "role": "Хозяин таверны «Пьяный Грифон»",
         "text": "Эль, горячий ужин или комната на ночь?",
         "portrait_color": (180, 120, 80)},
        {"speaker": "Олаф",
         "role": "Хозяин таверны «Пьяный Грифон»",
         "text": "За новостями — к завсегдатаям у камина.",
         "portrait_color": (180, 120, 80)},
    ]
    npc = NPC(0, 0, "Трактирщик Олаф", appearance, dialogues, "innkeeper")
    npc.appearance = appearance  # <-- ДОБАВИТЬ
    return npc


def create_guild_master() -> NPC:
    appearance = NPCAppearance(
        body_color=(70, 60, 100), skin_color=(225, 185, 155),
        hair_color=(50, 50, 60), hair_style="ponytail",
        outfit_color=(80, 70, 120), accessory="cape"
    )
    dialogues = [
        {"speaker": "Селина",
         "role": "Магистр Гильдии Искателей",
         "text": "Ты должно быть новый рекрут.",
         "portrait_color": (200, 150, 100)},
        {"speaker": "Селина",
         "role": "Магистр Гильдии Искателей",
         "text": "Гильдия Искателей — это честь и ответственность.",
         "portrait_color": (200, 150, 100)},
        {"speaker": "Селина",
         "role": "Магистр Гильдии Искателей",
         "text": "Докажи свою ценность, и двери откроются.",
         "portrait_color": (200, 150, 100)},
    ]
    npc = NPC(0, 0, "Магистр Селина", appearance, dialogues, "guild_master")
    npc.appearance = appearance  # <-- ДОБАВИТЬ
    return npc


def create_guard() -> NPC:
    appearance = NPCAppearance(
        body_color=(80, 80, 90), skin_color=(210, 175, 145),
        hair_color=(40, 35, 30), hair_style="short",
        outfit_color=(100, 100, 110), hat_color=(80, 80, 90), has_hat=True
    )
    dialogues = [
        {"speaker": "Стражник",
         "role": "Городская стража Валенхольма",
         "text": "Добро пожаловать в Валенхольм.",
         "portrait_color": (120, 120, 140)},
        {"speaker": "Стражник",
         "role": "Городская стража Валенхольма",
         "text": "Веди себя прилично — и проблем не будет.",
         "portrait_color": (120, 120, 140)},
    ]
    npc = NPC(0, 0, "Стражник", appearance, dialogues, "guard")
    npc.appearance = appearance  # <-- ДОБАВИТЬ
    return npc


def create_old_man() -> NPC:
    appearance = NPCAppearance(
        body_color=(100, 90, 120), skin_color=(215, 185, 165),
        hair_color=(200, 200, 200), hair_style="long",
        outfit_color=(90, 80, 110), has_beard=True, accessory="hood"
    )
    dialogues = [
        {"speaker": "Аэлрон",
         "role": "Хранитель древних знаний",
         "text": "А, молодой путник... Я ждал тебя.",
         "portrait_color": (180, 160, 220)},
        {"speaker": "Аэлрон",
         "role": "Хранитель древних знаний",
         "text": "Звёзды предрекли твоё появление.",
         "portrait_color": (180, 160, 220)},
        {"speaker": "Аэлрон",
         "role": "Хранитель древних знаний",
         "text": "Ищи Хранителей Памяти, если хочешь ответы.",
         "portrait_color": (180, 160, 220)},
    ]
    npc = NPC(0, 0, "Мудрец Аэлрон", appearance, dialogues, "sage")
    npc.appearance = appearance  # <-- ДОБАВИТЬ
    return npc


def create_barmaid() -> NPC:
    appearance = NPCAppearance(
        body_color=(140, 80, 80), skin_color=(240, 210, 185),
        hair_color=(180, 100, 60), hair_style="ponytail",
        outfit_color=(150, 90, 90), accessory="apron"
    )
    dialogues = [
        {"speaker": "Лина",
         "role": "Барменша таверны «Пьяный Грифон»",
         "text": "Чего желаете? Эль или что покрепче?",
         "portrait_color": (200, 130, 130)},
        {"speaker": "Лина",
         "role": "Барменша таверны «Пьяный Грифон»",
         "text": "Слышали новости? В лесу опять видели волков.",
         "portrait_color": (200, 130, 130)},
    ]
    npc = NPC(0, 0, "Барменша Лина", appearance, dialogues, "barmaid")
    npc.appearance = appearance  # <-- ДОБАВИТЬ
    return npc


def create_villager(name: str = "Житель") -> NPC:
    hair_styles = ["short", "long", "bald", "ponytail"]
    colors = [
        ((100, 80, 70), (80, 60, 50)),
        ((80, 100, 80), (60, 80, 60)),
        ((100, 90, 100), (80, 70, 80)),
        ((90, 80, 100), (70, 60, 80)),
    ]
    color_set = random.choice(colors)
    appearance = NPCAppearance(
        body_color=color_set[0],
        skin_color=(random.randint(200, 240), random.randint(160, 200), random.randint(140, 180)),
        hair_color=(random.randint(30, 100), random.randint(20, 70), random.randint(10, 50)),
        hair_style=random.choice(hair_styles),
        outfit_color=color_set[1],
        has_beard=random.random() < 0.3,
    )
    dialogues = [
        {"speaker": name,
         "role": "Житель Валенхольма",
         "text": random.choice([
             "Прекрасный день, не так ли?",
             "У Гильдии всегда есть работа для таких как ты.",
             "Остерегайся Туманного леса после заката.",
             "В таверне подают отличный эль!",
             "Слышал, в подземельях нашли древние руны...",
         ]),
         "portrait_color": (150, 130, 120)},
    ]
    npc = NPC(0, 0, name, appearance, dialogues, "villager")
    npc.appearance = appearance  # <-- ДОБАВИТЬ
    return npc


# Словарь всех типов NPC для теста
NPC_TYPES = {
    "blacksmith": ("Кузнец", create_blacksmith),
    "merchant": ("Торговец", create_merchant),
    "innkeeper": ("Трактирщик", create_innkeeper),
    "guild_master": ("Магистр гильдии", create_guild_master),
    "guard": ("Стражник", create_guard),
    "sage": ("Мудрец", create_old_man),
    "barmaid": ("Барменша", create_barmaid),
    "villager": ("Житель", lambda: create_villager("Житель")),
}