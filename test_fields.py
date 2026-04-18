"""
Тест: поля с переходом в город.
Запуск: python test_fields.py

Примечание: для полного опыта с переходами используйте test_world.py
Этот файл запускает только поля отдельно.
"""

import pygame
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.world.player import Player
from game.world.fields import FieldsMap
from game.world.dialogue import DialogueBox
from game.ui.notifications import NotificationManager
from game.menu.icons import Icons
from game.world.npc import NPC, NPCAppearance, create_guard, create_villager


def create_field_npcs():
    npcs = []
    farmer = create_villager("Фермер Борис")
    farmer.x, farmer.y = 430, 500
    farmer.appearance.outfit_color = (85, 100, 70)
    farmer.appearance.has_hat = True
    farmer.dialogues = [
        {"speaker": "Фермер Борис",
         "text": "Добро пожаловать на мои поля!",
         "portrait_color": (140, 160, 110)},
    ]
    npcs.append(farmer)

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
         "text": "Мои овечки пасутся за холмом!",
         "portrait_color": (150, 135, 120)},
    ], "shepherd")
    npcs.append(shepherd)

    girl_app = NPCAppearance(
        body_color=(140, 110, 130), skin_color=(235, 210, 190),
        hair_color=(180, 130, 70), hair_style="ponytail",
        outfit_color=(150, 120, 140),
    )
    girl = NPC(550, 620, "Девочка Мия", girl_app, [
        {"speaker": "Мия", "text": "Привет! Ты ловишь бабочек?",
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
         "text": "В лесу стало неспокойно.",
         "portrait_color": (130, 115, 100)},
    ], "hunter")
    npcs.append(hunter)

    guard = create_guard()
    guard.x, guard.y = 50, 720
    guard.name = "Стражник дороги"
    guard.dialogues = [
        {"speaker": "Стражник дороги",
         "text": "Дорога ведёт обратно в Валенхольм.",
         "portrait_color": (120, 120, 140)},
    ]
    npcs.append(guard)

    return npcs


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Тест полей — Echoes of the Fallen")

    clock = pygame.time.Clock()
    fields = FieldsMap()
    player = Player(300, 730)
    notifications = NotificationManager(screen)
    dialogue = DialogueBox(screen)
    field_npcs = create_field_npcs()

    camera_x, camera_y = 0.0, 0.0

    font_hint  = pygame.font.SysFont("segoeui", 14)
    font_small = pygame.font.SysFont("segoeui", 12)
    font_loc   = pygame.font.SysFont("segoeui", 14)
    font_debug = pygame.font.SysFont("segoeui", 13)

    show_debug = False
    talked = set()

    notifications.show_info("Поля Валенхольма", title="Локация")
    notifications.show_warning("Для теста с переходами: python test_world.py")

    def update_camera():
        nonlocal camera_x, camera_y
        sw, sh = screen.get_size()
        tx = player.x - sw // 2 + player.width // 2
        ty = player.y - sh // 2 + player.height // 2
        camera_x += (tx - camera_x) * 0.1
        camera_y += (ty - camera_y) * 0.1
        camera_x = max(0, min(camera_x, fields.width - sw))
        camera_y = max(0, min(camera_y, fields.height - sh))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if dialogue.active:
                dialogue.handle_event(event)
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_F1:
                    show_debug = not show_debug
                if event.key == pygame.K_e:
                    for npc in field_npcs:
                        if npc.hovered:
                            nid = id(npc)
                            if nid not in talked:
                                talked.add(nid)
                                notifications.show_achievement(
                                    f"Знакомство: {npc.name}",
                                    f"Вы поговорили с {npc.name}",
                                    Icons.draw_trophy)
                            dialogue.start_dialogue(npc.get_dialogues())
                            break

        dialogue.update(dt)
        notifications.update(dt)
        fields.update(player.feet_rect, dt)
        for npc in field_npcs:
            npc.update(dt, player.feet_rect)

        if not dialogue.active:
            keys = pygame.key.get_pressed()
            dx, dy = player.handle_input(keys, {})
            player.update(dt, dx, dy, fields.colliders)

        update_camera()

        sw, sh = screen.get_size()
        for y in range(sh):
            ratio = y / sh
            pygame.draw.line(screen, (int(130 + ratio * 40),
                                       int(180 + ratio * 30),
                                       int(230 - ratio * 30)), (0, y), (sw, y))

        fields.draw(screen, camera_x, camera_y, sw, sh)

        drawables = [(npc.y + npc.height, "npc", npc) for npc in field_npcs]
        drawables.append((player.y + player.height, "player", None))
        drawables.sort(key=lambda d: d[0])
        for _, kind, obj in drawables:
            if kind == "npc":
                obj.draw(screen, camera_x, camera_y)
            else:
                player.draw(screen, camera_x, camera_y)

        # HUD
        loc_s = font_loc.render("Поля Валенхольма", True, COLOR_TEXT_DIM)
        lbg = pygame.Surface((loc_s.get_width() + 20, 24), pygame.SRCALPHA)
        pygame.draw.rect(lbg, (18, 15, 28, 190), lbg.get_rect(), border_radius=5)
        screen.blit(lbg, (15, 15))
        screen.blit(loc_s, (25, 19))

        hs = font_hint.render("WASD — движение  |  E — говорить  |  ESC — выход",
                              True, COLOR_TEXT_DIM)
        hbg = pygame.Surface((hs.get_width() + 20, 24), pygame.SRCALPHA)
        pygame.draw.rect(hbg, (18, 15, 28, 160), hbg.get_rect(), border_radius=5)
        screen.blit(hbg, (sw // 2 - hbg.get_width() // 2, sh - 38))
        screen.blit(hs, (sw // 2 - hs.get_width() // 2, sh - 34))

        if show_debug:
            lines = [f"Pos: ({int(player.x)}, {int(player.y)})",
                     f"FPS: {int(clock.get_fps())}"]
            for i, l in enumerate(lines):
                screen.blit(font_debug.render(l, True, COLOR_TEXT_DIM), (15, 50 + i * 18))

        dialogue.draw()
        notifications.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()