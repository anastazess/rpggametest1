"""
Тест: город + поля с переходами между ними.
Запуск: python test_world.py
"""

import pygame
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.world.player import Player
from game.world.game_map import GameMap, PLAYER_SPAWN_X, PLAYER_SPAWN_Y
from game.world.fields import FieldsMap
from game.world.dialogue import DialogueBox
from game.world.interiors import get_interior
from game.ui.notifications import NotificationManager
from game.menu.icons import Icons
from game.world.npc import NPC, NPCAppearance, create_guard, create_villager


# ══════════════════════════════════════════════════════════════════════
# NPC для полей (копия из test_fields.py чтобы файл был автономным)
# ══════════════════════════════════════════════════════════════════════

def create_field_npcs():
    npcs = []

    farmer = create_villager("Фермер Борис")
    farmer.x, farmer.y = 430, 500
    farmer.appearance.outfit_color = (85, 100, 70)
    farmer.appearance.has_hat = True
    farmer.appearance.hat_color = (70, 85, 55)
    farmer.dialogues = [
        {"speaker": "Фермер Борис",
         "text": "Добро пожаловать на мои поля! Урожай в этом году отменный.",
         "portrait_color": (140, 160, 110)},
        {"speaker": "Фермер Борис",
         "text": "Только волки повадились таскать овец...",
         "portrait_color": (140, 160, 110)},
    ]
    npcs.append(farmer)

    wife = create_villager("Анна")
    wife.x, wife.y = 480, 480
    wife.appearance.hair_style = "long"
    wife.appearance.outfit_color = (120, 90, 80)
    wife.dialogues = [
        {"speaker": "Анна",
         "text": "Здравствуй, путник! Хочешь свежего хлеба?",
         "portrait_color": (180, 140, 120)},
    ]
    npcs.append(wife)

    miller_app = NPCAppearance(
        body_color=(100, 90, 80), skin_color=(220, 185, 160),
        hair_color=(180, 170, 160), hair_style="bald",
        outfit_color=(110, 100, 90), has_beard=True, accessory="apron",
    )
    miller = NPC(1280, 350, "Мельник Густав", miller_app, [
        {"speaker": "Мельник Густав",
         "text": "Моя мельница работает день и ночь!",
         "portrait_color": (170, 150, 130)},
    ], "miller")
    npcs.append(miller)

    shepherd_app = NPCAppearance(
        body_color=(90, 85, 75), skin_color=(215, 180, 155),
        hair_color=(100, 75, 50), hair_style="short",
        outfit_color=(100, 95, 80), has_hat=True, hat_color=(80, 75, 60),
    )
    shepherd = NPC(900, 1100, "Пастух Ян", shepherd_app, [
        {"speaker": "Пастух Ян",
         "text": "Мои овечки пасутся за холмом. Не пугай их!",
         "portrait_color": (150, 135, 120)},
    ], "shepherd")
    npcs.append(shepherd)

    girl_app = NPCAppearance(
        body_color=(140, 110, 130), skin_color=(235, 210, 190),
        hair_color=(180, 130, 70), hair_style="ponytail",
        outfit_color=(150, 120, 140),
    )
    girl = NPC(550, 620, "Девочка Мия", girl_app, [
        {"speaker": "Мия",
         "text": "Привет! Ты тоже пришёл ловить бабочек?",
         "portrait_color": (190, 160, 180)},
    ], "child")
    npcs.append(girl)

    hunter_app = NPCAppearance(
        body_color=(70, 65, 55), skin_color=(200, 170, 145),
        hair_color=(50, 40, 30), hair_style="short",
        outfit_color=(80, 75, 60), has_beard=True, accessory="hood",
    )
    hunter = NPC(1600, 420, "Охотник Рейн", hunter_app, [
        {"speaker": "Охотник Рейн",
         "text": "Я только что из Туманного леса. Там стало неспокойно.",
         "portrait_color": (130, 115, 100)},
    ], "hunter")
    npcs.append(hunter)

    road_guard = create_guard()
    road_guard.x, road_guard.y = 50, 720
    road_guard.name = "Стражник дороги"
    road_guard.dialogues = [
        {"speaker": "Стражник дороги",
         "text": "Эта дорога ведёт обратно в Валенхольм.",
         "portrait_color": (120, 120, 140)},
    ]
    npcs.append(road_guard)

    return npcs


# ══════════════════════════════════════════════════════════════════════
# Зоны перехода
# ══════════════════════════════════════════════════════════════════════

class TransitionZone:
    """Зона перехода между локациями."""

    def __init__(self, rect, target_location, spawn_x, spawn_y, label):
        self.rect = rect
        self.target = target_location   # "city" или "fields"
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.label = label
        self.player_near = False
        self.pulse = 0.0

        self.font = pygame.font.SysFont("segoeui", 13, bold=True)

    def update(self, player_rect, dt):
        self.player_near = self.rect.inflate(40, 40).colliderect(player_rect)
        self.pulse += dt * 3

    def check_trigger(self, player_rect):
        return self.rect.colliderect(player_rect)

    def draw(self, surface, camera_x, camera_y):
        sx = int(self.rect.x - camera_x)
        sy = int(self.rect.y - camera_y)
        w = self.rect.width
        h = self.rect.height

        # Полупрозрачная зона
        alpha = int(80 + 40 * math.sin(self.pulse))
        zone_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(zone_surf, (255, 200, 50, alpha),
                         (0, 0, w, h), border_radius=6)
        pygame.draw.rect(zone_surf, (255, 200, 50, min(alpha + 60, 220)),
                         (0, 0, w, h), width=2, border_radius=6)
        surface.blit(zone_surf, (sx, sy))

        # Стрелка
        arrow_x = sx + w // 2
        arrow_y = sy - 15
        arrow_bob = int(math.sin(self.pulse * 1.5) * 4)
        points = [
            (arrow_x, arrow_y + arrow_bob - 8),
            (arrow_x - 8, arrow_y + arrow_bob),
            (arrow_x + 8, arrow_y + arrow_bob),
        ]
        pygame.draw.polygon(surface, (255, 220, 80), points)

        # Подсказка
        if self.player_near:
            hint = f"[Подойди ближе] {self.label}"
            hint_surf = self.font.render(hint, True, COLOR_ACCENT)
            hx = sx + w // 2 - hint_surf.get_width() // 2
            hy = sy - 35 + arrow_bob

            bg = pygame.Surface((hint_surf.get_width() + 16, 22), pygame.SRCALPHA)
            pygame.draw.rect(bg, (20, 18, 30, 210), bg.get_rect(), border_radius=5)
            surface.blit(bg, (hx - 8, hy - 2))
            surface.blit(hint_surf, (hx, hy))


# ══════════════════════════════════════════════════════════════════════
# Основная функция
# ══════════════════════════════════════════════════════════════════════

def main():
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Тест мира — Echoes of the Fallen")

    clock = pygame.time.Clock()

    # ── Создаём обе локации ──────────────────────────────────────────
    city_map = GameMap()
    fields_map = FieldsMap()
    field_npcs = create_field_npcs()

    player = Player(PLAYER_SPAWN_X, PLAYER_SPAWN_Y)
    notifications = NotificationManager(screen)
    dialogue = DialogueBox(screen)

    camera_x, camera_y = 0.0, 0.0

    # Состояние
    current_location = "city"   # "city" | "fields" | "interior"
    current_interior = None
    interior_cam_x = 0.0
    interior_cam_y = 0.0
    interior_prev_pos = (0, 0)

    # ── Зоны перехода ────────────────────────────────────────────────
    # Город → Поля (правый край города)
    city_to_fields = TransitionZone(
        pygame.Rect(city_map.width - 40, 490, 40, 120),
        "fields", 40, 720,     # Спавн на левом краю полей
        "→ К полям Валенхольма"
    )
    # Поля → Город (левый край полей)
    fields_to_city = TransitionZone(
        pygame.Rect(0, 690, 40, 100),
        "city", city_map.width - 80, 530,  # Спавн у правого края города
        "← В Валенхольм"
    )

    font_title = pygame.font.SysFont("georgia", 22, bold=True)
    font_hint  = pygame.font.SysFont("segoeui", 14)
    font_small = pygame.font.SysFont("segoeui", 12)
    font_debug = pygame.font.SysFont("segoeui", 13)
    font_loc   = pygame.font.SysFont("segoeui", 14)

    show_debug = False
    visited_buildings = set()
    visited_npcs = set()

    notifications.show_info("Добро пожаловать в Валенхольм!", title="Город")

    # ── Вспомогательные функции ──────────────────────────────────────

    def get_current_map():
        if current_location == "city":
            return city_map
        elif current_location == "fields":
            return fields_map
        return None

    def get_current_npcs():
        if current_location == "city":
            return city_map.street_npcs
        elif current_location == "fields":
            return field_npcs
        return []

    def get_current_transitions():
        if current_location == "city":
            return [city_to_fields]
        elif current_location == "fields":
            return [fields_to_city]
        return []

    def update_camera():
        nonlocal camera_x, camera_y
        cmap = get_current_map()
        if cmap is None:
            return
        sw, sh = screen.get_size()
        tx = player.x - sw // 2 + player.width // 2
        ty = player.y - sh // 2 + player.height // 2
        camera_x += (tx - camera_x) * 0.12
        camera_y += (ty - camera_y) * 0.12
        camera_x = max(0, min(camera_x, cmap.width - sw))
        camera_y = max(0, min(camera_y, cmap.height - sh))

    def do_transition(zone):
        nonlocal current_location, camera_x, camera_y
        old = current_location
        current_location = zone.target
        player.x = float(zone.spawn_x)
        player.y = float(zone.spawn_y)
        camera_x = player.x - 640
        camera_y = player.y - 360

        loc_name = "Валенхольм" if zone.target == "city" else "Поля Валенхольма"
        notifications.show_info(f"Вы прибыли: {loc_name}", title="Переход")

    def enter_building(building):
        nonlocal current_location, current_interior, interior_cam_x, interior_cam_y, interior_prev_pos
        interior = get_interior(building.name)
        if interior is None:
            notifications.show_warning("Здание пока недоступно")
            return
        interior_prev_pos = (player.x, player.y)
        ep = interior.entry_point
        player.x = float(ep[0] - player.width // 2)
        player.y = float(ep[1] - player.height)
        interior_cam_x = 0.0
        interior_cam_y = 0.0
        current_interior = interior
        current_location = "interior"
        name = building.name
        if name not in visited_buildings:
            visited_buildings.add(name)
            notifications.show_achievement(f"Открыто: {name}",
                                           f"Вы посетили {name}", Icons.draw_trophy)
        else:
            notifications.show_info(f"Вы вошли в {name}", title=name)

    def exit_building():
        nonlocal current_location, current_interior
        player.x = float(interior_prev_pos[0])
        player.y = float(interior_prev_pos[1] + 20)
        current_interior = None
        current_location = "city"
        notifications.show_info("Вы вышли на улицу")

    def draw_minimap():
        cmap = get_current_map()
        if cmap is None:
            return
        sw, _ = screen.get_size()
        mw, mh = 180, 125
        mx, my = sw - mw - 12, 12

        mm = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.rect(mm, (18, 15, 28, 215), (0, 0, mw, mh), border_radius=8)
        pygame.draw.rect(mm, (*COLOR_PRIMARY_DARK, 160), (0, 0, mw, mh),
                         width=1, border_radius=8)

        sx = (mw - 10) / cmap.width
        sy = (mh - 10) / cmap.height

        for road in cmap.roads:
            pygame.draw.rect(mm, (70, 60, 50),
                             (5 + int(road.x * sx), 5 + int(road.y * sy),
                              max(2, int(road.width * sx)),
                              max(2, int(road.height * sy))))

        if hasattr(cmap, 'buildings'):
            for b in cmap.buildings:
                bx = 5 + int(b.x * sx)
                by = 5 + int(b.y * sy)
                bw = max(3, int(b.width * sx))
                bh = max(3, int(b.height * sy))
                pygame.draw.rect(mm, (160, 110, 80), (bx, by, bw, bh))

        if hasattr(cmap, 'wheat_fields'):
            for wf in cmap.wheat_fields:
                pygame.draw.rect(mm, (160, 145, 70),
                                 (5 + int(wf.x * sx), 5 + int(wf.y * sy),
                                  max(2, int(wf.width * sx)),
                                  max(2, int(wf.height * sy))))

        for npc in get_current_npcs():
            nx = 5 + int(npc.x * sx)
            ny = 5 + int(npc.y * sy)
            pygame.draw.circle(mm, (100, 200, 255), (nx, ny), 2)

        # Зоны перехода
        for tz in get_current_transitions():
            tx = 5 + int(tz.rect.x * sx)
            ty = 5 + int(tz.rect.y * sy)
            tw = max(3, int(tz.rect.width * sx))
            th = max(3, int(tz.rect.height * sy))
            pygame.draw.rect(mm, (255, 200, 50), (tx, ty, tw, th))

        px = 5 + int(player.x * sx)
        py = 5 + int(player.y * sy)
        pygame.draw.circle(mm, COLOR_ACCENT, (px, py), 3)

        screen.blit(mm, (mx, my))
        loc_name = "Валенхольм" if current_location == "city" else "Поля"
        cap = font_small.render(loc_name, True, COLOR_TEXT_DIM)
        screen.blit(cap, (mx + mw // 2 - cap.get_width() // 2, my + mh + 3))

    def draw_hud():
        sw, sh = screen.get_size()
        loc_names = {"city": "Валенхольм", "fields": "Поля Валенхольма",
                     "interior": current_interior.name if current_interior else ""}
        loc_text = loc_names.get(current_location, "")
        loc_surf = font_loc.render(loc_text, True, COLOR_TEXT_DIM)
        loc_bg = pygame.Surface((loc_surf.get_width() + 20, 24), pygame.SRCALPHA)
        pygame.draw.rect(loc_bg, (18, 15, 28, 190), loc_bg.get_rect(), border_radius=5)
        screen.blit(loc_bg, (15, 15))
        screen.blit(loc_surf, (25, 19))

        hints = ["WASD — движение", "E — взаимодействие", "F1 — отладка", "ESC — выход"]
        if current_location == "interior":
            hints.insert(2, "ESC — выйти из здания")
        hint_text = "  |  ".join(hints)
        hs = font_hint.render(hint_text, True, COLOR_TEXT_DIM)
        hbg = pygame.Surface((hs.get_width() + 20, 24), pygame.SRCALPHA)
        pygame.draw.rect(hbg, (18, 15, 28, 160), hbg.get_rect(), border_radius=5)
        screen.blit(hbg, (sw // 2 - hbg.get_width() // 2, sh - 38))
        screen.blit(hs, (sw // 2 - hs.get_width() // 2, sh - 34))

    def draw_debug():
        if not show_debug:
            return
        lines = [
            f"Локация: {current_location}",
            f"Позиция: ({int(player.x)}, {int(player.y)})",
            f"Камера: ({int(camera_x)}, {int(camera_y)})",
            f"FPS: {int(clock.get_fps())}",
        ]
        ph = len(lines) * 18 + 14
        panel = pygame.Surface((250, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (18, 15, 28, 215), (0, 0, 250, ph), border_radius=6)
        screen.blit(panel, (12, 50))
        for i, line in enumerate(lines):
            screen.blit(font_debug.render(line, True, COLOR_TEXT_DIM), (20, 57 + i * 18))

    # ══════════════════════════════════════════════════════════════════
    # Главный цикл
    # ══════════════════════════════════════════════════════════════════

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # ── События ──────────────────────────────────────────────────

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if dialogue.active:
                dialogue.handle_event(event)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_location == "interior":
                        exit_building()
                    else:
                        running = False

                if event.key == pygame.K_F1:
                    show_debug = not show_debug

                if event.key == pygame.K_e:
                    if current_location == "interior":
                        npc = current_interior.get_hovered_npc()
                        if npc and npc.dialogues:
                            dialogue.start_dialogue(npc.get_dialogues())

                    elif current_location == "city":
                        npc = city_map.get_hovered_npc()
                        if npc:
                            nid = id(npc)
                            if nid not in visited_npcs:
                                visited_npcs.add(nid)
                                notifications.show_achievement(
                                    f"Знакомство: {npc.name}",
                                    f"Вы поговорили с {npc.name}",
                                    Icons.draw_trophy)
                            dialogue.start_dialogue(npc.get_dialogues())
                        else:
                            building = city_map.get_hovered_building()
                            if building:
                                enter_building(building)

                    elif current_location == "fields":
                        for npc in field_npcs:
                            if npc.hovered:
                                nid = id(npc)
                                if nid not in visited_npcs:
                                    visited_npcs.add(nid)
                                    notifications.show_achievement(
                                        f"Знакомство: {npc.name}",
                                        f"Вы поговорили с {npc.name}",
                                        Icons.draw_trophy)
                                dialogue.start_dialogue(npc.get_dialogues())
                                break

        # ── Обновление ───────────────────────────────────────────────

        dialogue.update(dt)
        notifications.update(dt)

        if not dialogue.active:
            keys = pygame.key.get_pressed()
            dx, dy = player.handle_input(keys, {})

            if current_location == "city":
                player.update(dt, dx, dy, city_map.colliders)
                city_map.update(player.feet_rect, dt)

                city_to_fields.update(player.feet_rect, dt)
                if city_to_fields.check_trigger(player.feet_rect):
                    do_transition(city_to_fields)

            elif current_location == "fields":
                player.update(dt, dx, dy, fields_map.colliders)
                fields_map.update(player.feet_rect, dt)
                for npc in field_npcs:
                    npc.update(dt, player.feet_rect)

                fields_to_city.update(player.feet_rect, dt)
                if fields_to_city.check_trigger(player.feet_rect):
                    do_transition(fields_to_city)

            elif current_location == "interior":
                player.update(dt, dx, dy, current_interior.colliders)
                current_interior.update(dt, player.feet_rect)
                if player.y > current_interior.height - 20:
                    exit_building()

        # Камера
        if current_location in ("city", "fields"):
            update_camera()
        elif current_location == "interior":
            sw, sh = screen.get_size()
            tx = player.x - sw // 2 + player.width // 2
            ty = player.y - sh // 2 + player.height // 2
            interior_cam_x += (tx - interior_cam_x) * 0.12
            interior_cam_y += (ty - interior_cam_y) * 0.12
            interior_cam_x = max(0, min(interior_cam_x,
                                        max(0, current_interior.width - sw)))
            interior_cam_y = max(0, min(interior_cam_y,
                                        max(0, current_interior.height - sh)))

        # ── Отрисовка ────────────────────────────────────────────────

        sw, sh = screen.get_size()

        if current_location == "city":
            city_map.draw(screen, camera_x, camera_y, sw, sh)
            player.draw(screen, camera_x, camera_y)
            city_to_fields.draw(screen, camera_x, camera_y)

        elif current_location == "fields":
            # Небо
            for y in range(sh):
                ratio = y / sh
                r = int(130 + ratio * 40)
                g = int(180 + ratio * 30)
                b = int(230 - ratio * 30)
                pygame.draw.line(screen, (r, g, b), (0, y), (sw, y))

            fields_map.draw(screen, camera_x, camera_y, sw, sh)

            # NPC + игрок с сортировкой
            drawables = []
            for npc in field_npcs:
                drawables.append((npc.y + npc.height, "npc", npc))
            drawables.append((player.y + player.height, "player", None))
            drawables.sort(key=lambda d: d[0])
            for _, kind, obj in drawables:
                if kind == "npc":
                    obj.draw(screen, camera_x, camera_y)
                elif kind == "player":
                    player.draw(screen, camera_x, camera_y)

            fields_to_city.draw(screen, camera_x, camera_y)

        elif current_location == "interior":
            interior = current_interior
            cx, cy = interior_cam_x, interior_cam_y
            screen.blit(interior.get_ground(), (-cx, -cy))

            drawables = []
            for furn in interior.furniture:
                drawables.append((furn.y + furn.height, "furn", furn))
            for npc in interior.npcs:
                drawables.append((npc.y + npc.height, "npc", npc))
            drawables.append((player.y + player.height, "player", None))
            drawables.sort(key=lambda d: d[0])

            for _, kind, obj in drawables:
                if kind == "furn":
                    interior._draw_furniture(screen, obj, cx, cy)
                elif kind == "npc":
                    obj.draw(screen, cx, cy)
                elif kind == "player":
                    player.draw(screen, cx, cy)

            bx, by = int(-cx), int(-cy)
            pygame.draw.rect(screen, COLOR_PRIMARY_DARK,
                             (bx, by, interior.width, interior.height), width=2)
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            room = pygame.Rect(bx, by, interior.width, interior.height)
            for dim in [
                pygame.Rect(0, 0, sw, max(0, room.top)),
                pygame.Rect(0, room.bottom, sw, max(0, sh - room.bottom)),
                pygame.Rect(0, 0, max(0, room.left), sh),
                pygame.Rect(room.right, 0, max(0, sw - room.right), sh),
            ]:
                if dim.width > 0 and dim.height > 0:
                    pygame.draw.rect(overlay, (0, 0, 0, 200), dim)
            screen.blit(overlay, (0, 0))

        draw_hud()
        if current_location != "interior":
            draw_minimap()
        draw_debug()
        dialogue.draw()
        notifications.draw()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()