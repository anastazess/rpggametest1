"""
Тест: свободная прогулка по игровому миру.
Запуск: python test_world.py
"""

import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.world.player import Player
from game.world.game_map import GameMap, PLAYER_SPAWN_X, PLAYER_SPAWN_Y
from game.ui.notifications import NotificationManager
from game.menu.icons import Icons
from game.world.interiors import get_interior
from game.world.dialogue import DialogueBox


def main():
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Тест мира — Echoes of the Fallen")

    clock  = pygame.time.Clock()
    player = Player(PLAYER_SPAWN_X, PLAYER_SPAWN_Y)
    gmap   = GameMap()
    # Интерьер
    current_interior = None
    interior_cam_x = 0.0
    interior_cam_y = 0.0
    interior_prev_pos = (PLAYER_SPAWN_X, PLAYER_SPAWN_Y)
    interior_state = "world"  # "world" | "interior"

    dialogue = DialogueBox(screen)
    notifications = NotificationManager(screen)

    camera_x, camera_y = 0.0, 0.0

    font_debug = pygame.font.SysFont("segoeui", 15)
    font_title = pygame.font.SysFont("georgia", 22, bold=True)
    font_hint  = pygame.font.SysFont("segoeui", 14)
    font_small = pygame.font.SysFont("segoeui", 12)

    show_debug = False
    visited_buildings = set()
    visited_npcs = set()

    # Первое уведомление
    notifications.show_info("Используй WASD для движения", title="Управление")

    # ── Камера ───────────────────────────────────────────────────────
    def update_camera():
        nonlocal camera_x, camera_y
        sw, sh = screen.get_size()
        tx = player.x - sw // 2 + player.width  // 2
        ty = player.y - sh // 2 + player.height // 2
        camera_x += (tx - camera_x) * 0.12
        camera_y += (ty - camera_y) * 0.12
        camera_x = max(0, min(camera_x, gmap.width  - sw))
        camera_y = max(0, min(camera_y, gmap.height - sh))

    # ── Мини-карта ───────────────────────────────────────────────────
    def draw_minimap():
        sw, _ = screen.get_size()
        mw, mh = 180, 120
        mx, my = sw - mw - 12, 12

        mm = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.rect(mm, (18, 15, 28, 215),
                         (0, 0, mw, mh), border_radius=8)
        pygame.draw.rect(mm, (*COLOR_PRIMARY_DARK, 160),
                         (0, 0, mw, mh), width=1, border_radius=8)

        sx = (mw - 10) / gmap.width
        sy = (mh - 10) / gmap.height

        # Дороги
        for road in gmap.roads:
            pygame.draw.rect(mm, (70, 60, 50),
                             (5 + int(road.x * sx), 5 + int(road.y * sy),
                              max(2, int(road.width  * sx)),
                              max(2, int(road.height * sy))))

        # Здания
        for b in gmap.buildings:
            bx_ = 5 + int(b.x * sx)
            by_ = 5 + int(b.y * sy)
            bw  = max(3, int(b.width  * sx))
            bh  = max(3, int(b.height * sy))
            pygame.draw.rect(mm, (160, 110, 80), (bx_, by_, bw, bh))

        # NPC (уличные)
        for npc in gmap.street_npcs:
            nx_ = 5 + int(npc.x * sx)
            ny_ = 5 + int(npc.y * sy)
            pygame.draw.circle(mm, (100, 200, 255), (nx_, ny_), 2)

        # Игрок
        px_ = 5 + int(player.x * sx)
        py_ = 5 + int(player.y * sy)
        pygame.draw.circle(mm, COLOR_ACCENT, (px_, py_), 3)

        screen.blit(mm, (mx, my))

        cap = font_small.render("Карта  (● игрок  ● NPC)", True, COLOR_TEXT_DIM)
        screen.blit(cap, (mx, my + mh + 3))

    # ── HUD ──────────────────────────────────────────────────────────
    def draw_hud():
        sw, sh = screen.get_size()

        # Заголовок (локация)
        title_s = font_title.render("Тест мира — Валенхольм", True, COLOR_PRIMARY_LIGHT)
        bg = pygame.Surface((title_s.get_width() + 24, 32), pygame.SRCALPHA)
        pygame.draw.rect(bg, (18, 15, 28, 200), bg.get_rect(), border_radius=6)
        screen.blit(bg,      (12, 12))
        screen.blit(title_s, (24, 16))

        # Подсказки
        lines = [
            "WASD / стрелки — движение",
            "E — взаимодействие со зданием / NPC",
            "F1 — отладка  |  ESC — выход",
        ]
        hint_y = sh - len(lines) * 22 - 8
        for line in lines:
            hs  = font_hint.render(line, True, COLOR_TEXT_DIM)
            hbg = pygame.Surface((hs.get_width() + 14, 20), pygame.SRCALPHA)
            pygame.draw.rect(hbg, (18, 15, 28, 160), hbg.get_rect(), border_radius=4)
            screen.blit(hbg, (sw // 2 - hbg.get_width() // 2, hint_y))
            screen.blit(hs,  (sw // 2 - hs.get_width()  // 2, hint_y + 1))
            hint_y += 22

    # ── Отладка ───────────────────────────────────────────────────────
    def draw_debug():
        if not show_debug:
            return
        lines = [
            f"Позиция игрока: ({int(player.x)}, {int(player.y)})",
            f"Камера:         ({int(camera_x)}, {int(camera_y)})",
            f"Направление:    {player.direction}",
            f"Движение:       {player.moving}",
            f"Коллайдеров:    {len(gmap.colliders)}",
            f"Уличных NPC:    {len(gmap.street_npcs)}",
            f"Зданий:         {len(gmap.buildings)}",
            f"FPS:            {int(clock.get_fps())}",
        ]
        panel_h = len(lines) * 18 + 16
        panel = pygame.Surface((260, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (18, 15, 28, 215),
                         (0, 0, 260, panel_h), border_radius=6)
        pygame.draw.rect(panel, (*COLOR_PRIMARY_DARK, 120),
                         (0, 0, 260, panel_h), width=1, border_radius=6)
        screen.blit(panel, (12, 52))

        for i, line in enumerate(lines):
            s = font_debug.render(line, True, COLOR_TEXT_DIM)
            screen.blit(s, (20, 60 + i * 18))

    # ── Главный цикл ─────────────────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if interior_state == "interior":
                        # Выходим из интерьера
                        player.x = float(interior_prev_pos[0])
                        player.y = float(interior_prev_pos[1] + 20)
                        current_interior = None
                        interior_state = "world"
                        notifications.show_info("Вы вышли на улицу")
                    else:
                        running = False

                if event.key == pygame.K_F1:
                    show_debug = not show_debug
                    notifications.show_info(
                        "Отладка " + ("включена" if show_debug else "выключена"))

                if event.key == pygame.K_e:
                    if interior_state == "interior":
                        # Диалог с NPC внутри
                        if dialogue.active:
                            pass
                        else:
                            npc = current_interior.get_hovered_npc()
                            if npc and npc.dialogues:
                                dialogue.start_dialogue(npc.get_dialogues())
                    else:
                        # Диалог или вход в здание
                        if not dialogue.active:
                            npc = gmap.get_hovered_npc()
                            if npc:
                                npc_id = id(npc)
                                if npc_id not in visited_npcs:
                                    visited_npcs.add(npc_id)
                                    notifications.show_achievement(
                                        f"Знакомство: {npc.name}",
                                        f"Вы поговорили с {npc.name}",
                                        Icons.draw_trophy
                                    )
                                dialogue.start_dialogue(npc.get_dialogues())
                            else:
                                building = gmap.get_hovered_building()
                                if building:
                                    interior = get_interior(building.name)
                                    if interior:
                                        interior_prev_pos = (player.x, player.y)
                                        ep = interior.entry_point
                                        player.x = float(ep[0] - player.width // 2)
                                        player.y = float(ep[1] - player.height)
                                        interior_cam_x = 0.0
                                        interior_cam_y = 0.0
                                        current_interior = interior
                                        interior_state = "interior"
                                        name = building.name
                                        if name not in visited_buildings:
                                            visited_buildings.add(name)
                                            notifications.show_achievement(
                                                f"Открыто: {name}",
                                                f"Вы посетили {name}",
                                                Icons.draw_trophy
                                            )
                                        else:
                                            notifications.show_info(
                                                f"Вы вошли в {name}", title=name)
                                    else:
                                        notifications.show_warning(
                                            "Здание пока недоступно")

            # Диалог перехватывает клики
            if dialogue.active:
                dialogue.handle_event(event)

        # ── Обновление диалога ────────────────────────────────────────
        dialogue.update(dt)

        # ── Движение ─────────────────────────────────────────────────
        keys = pygame.key.get_pressed()

        if not dialogue.active:
            dx, dy = player.handle_input(keys, {})

            if interior_state == "world":
                player.update(dt, dx, dy, gmap.colliders)
                gmap.update(player.feet_rect, dt)

            elif interior_state == "interior":
                player.update(dt, dx, dy, current_interior.colliders)
                current_interior.update(dt, player.feet_rect)

                # Выход через дверь
                if player.y > current_interior.height - 20:
                    player.x = float(interior_prev_pos[0])
                    player.y = float(interior_prev_pos[1] + 20)
                    current_interior = None
                    interior_state = "world"
                    notifications.show_info("Вы вышли на улицу")

        # ── Камера ───────────────────────────────────────────────────
        if interior_state == "world":
            update_camera()
        else:
            # Камера внутри интерьера
            sw, sh = screen.get_size()
            tx = player.x - sw // 2 + player.width // 2
            ty = player.y - sh // 2 + player.height // 2
            interior_cam_x += (tx - interior_cam_x) * 0.12
            interior_cam_y += (ty - interior_cam_y) * 0.12
            interior_cam_x = max(0, min(interior_cam_x,
                                        max(0, current_interior.width - sw)))
            interior_cam_y = max(0, min(interior_cam_y,
                                        max(0, current_interior.height - sh)))

        notifications.update(dt)

        # ── Отрисовка ────────────────────────────────────────────────
        sw, sh = screen.get_size()

        if interior_state == "world":
            gmap.draw(screen, camera_x, camera_y, sw, sh)
            player.draw(screen, camera_x, camera_y)

        else:
            # Интерьер
            interior = current_interior
            cx = interior_cam_x
            cy = interior_cam_y

            ground = interior.get_ground()
            screen.blit(ground, (-cx, -cy))

            # Сортировка по Y
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

            # Рамка комнаты
            bx = int(-cx)
            by = int(-cy)
            pygame.draw.rect(screen, COLOR_PRIMARY_DARK,
                             (bx, by, interior.width, interior.height),
                             width=2)

            # Затемнение снаружи комнаты
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            room_rect = pygame.Rect(bx, by, interior.width, interior.height)
            for dim in [
                pygame.Rect(0, 0, sw, max(0, room_rect.top)),
                pygame.Rect(0, room_rect.bottom, sw,
                            max(0, sh - room_rect.bottom)),
                pygame.Rect(0, 0, max(0, room_rect.left), sh),
                pygame.Rect(room_rect.right, 0,
                            max(0, sw - room_rect.right), sh),
            ]:
                if dim.width > 0 and dim.height > 0:
                    pygame.draw.rect(overlay, (0, 0, 0, 200), dim)
            screen.blit(overlay, (0, 0))

            # Подсказка выхода
            exit_hint = font_hint.render(
                "ESC — выйти на улицу  |  E — говорить с NPC",
                True, COLOR_TEXT_DIM)
            ehbg = pygame.Surface(
                (exit_hint.get_width() + 20, 24), pygame.SRCALPHA)
            pygame.draw.rect(ehbg, (18, 15, 28, 180),
                             ehbg.get_rect(), border_radius=5)
            screen.blit(ehbg,
                        (sw // 2 - ehbg.get_width() // 2, sh - 35))
            screen.blit(exit_hint,
                        (sw // 2 - exit_hint.get_width() // 2, sh - 31))

        draw_hud()
        if interior_state == "world":
            draw_minimap()
        draw_debug()

        # Диалог поверх всего
        dialogue.draw()

        notifications.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()