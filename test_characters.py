"""
Тест: просмотр всех персонажей и NPC.
Запуск: python test_characters.py
"""

import pygame
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.world.npc import (
    NPC, NPCAppearance,
    create_blacksmith, create_merchant, create_innkeeper,
    create_guild_master, create_guard, create_old_man,
    create_barmaid, create_villager,
)
from game.world.player import Player


# ── Все персонажи ──────────────────────────────────────────────────────

def build_character_list():
    entries = []

    # Игрок
    p = Player(0, 0)
    entries.append({
        "name": "Главный герой",
        "type": "player",
        "role": "Протагонист",
        "obj": p,
        "is_player": True,
        "description": (
            "Очнулся без памяти у врат Валенхольма. "
            "Ищет ответы о своём прошлом."
        ),
    })

    # NPC с фабричными функциями
    npc_defs = [
        ("Кузнец Горан",     "blacksmith",   "Кузнец",          create_blacksmith),
        ("Торговец Браен",   "merchant",     "Торговец",        create_merchant),
        ("Трактирщик Олаф",  "innkeeper",    "Трактирщик",      create_innkeeper),
        ("Магистр Селина",   "guild_master", "Магистр гильдии", create_guild_master),
        ("Стражник",         "guard",        "Стражник",        create_guard),
        ("Мудрец Аэлрон",    "sage",         "Мудрец",          create_old_man),
        ("Барменша Лина",    "barmaid",      "Барменша",        create_barmaid),
    ]

    for name, npc_type, role, factory in npc_defs:
        npc = factory()
        npc.x, npc.y = 0, 0
        desc = npc.dialogues[0]["text"] if npc.dialogues else "—"
        entries.append({
            "name": name,
            "type": npc_type,
            "role": role,
            "obj": npc,
            "is_player": False,
            "description": desc,
        })

    # Случайные жители
    villager_names = [
        ("Фермер Том",      "villager", "Фермер"),
        ("Рыбак Олег",      "villager", "Рыбак"),
        ("Торговка Марта",  "villager", "Торговка"),
        ("Охотник Рейн",    "villager", "Охотник"),
        ("Пекарь Аня",      "villager", "Пекарь"),
    ]
    for name, npc_type, role in villager_names:
        npc = create_villager(name)
        npc.x, npc.y = 0, 0
        entries.append({
            "name": name,
            "type": npc_type,
            "role": role,
            "obj": npc,
            "is_player": False,
            "description": npc.dialogues[0]["text"] if npc.dialogues else "—",
        })

    return entries


# ── Вспомогательные функции рендера ───────────────────────────────────

def draw_character_to_surface(obj, is_player: bool,
                               direction: str, time_val: float,
                               surf_size: int = 80) -> pygame.Surface:
    """
    Рисует персонажа на отдельной поверхности и возвращает её.
    Никаких вызовов .update() — только .draw().
    """
    surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)

    # Временно ставим позицию в центр поверхности
    old_x = obj.x
    old_y = obj.y
    old_dir = obj.direction
    old_moving = obj.moving
    old_anim = obj.anim_time

    cx = surf_size // 2 - obj.width  // 2
    cy = surf_size // 2 - obj.height // 2 + 5

    obj.x       = cx
    obj.y       = cy
    obj.direction = direction
    obj.moving    = False
    obj.anim_time = time_val          # idle анимация

    obj.draw(surf, 0, 0)

    # Восстанавливаем
    obj.x       = old_x
    obj.y       = old_y
    obj.direction = old_dir
    obj.moving    = old_moving
    obj.anim_time = old_anim

    return surf


def wrap_text(text: str, font, max_w: int):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


# ── Главный экран ──────────────────────────────────────────────────────

def main():
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Галерея персонажей — Echoes of the Fallen")
    clock = pygame.time.Clock()

    # Шрифты
    font_title   = pygame.font.SysFont("georgia",  26, bold=True)
    font_heading = pygame.font.SysFont("segoeui",  17, bold=True)
    font_normal  = pygame.font.SysFont("segoeui",  14)
    font_small   = pygame.font.SysFont("segoeui",  12)
    font_tiny    = pygame.font.SysFont("segoeui",  11)

    characters   = build_character_list()
    selected     = 0
    time_acc     = 0.0

    # Направления для боковых превью
    DIRECTIONS   = ["down", "left", "right", "up"]

    # Генерируем статичный фон
    bg = pygame.Surface((1280, 720))
    for y in range(720):
        ratio = y / 720
        r = int(12 + ratio * 10)
        g = int(10 + ratio * 8)
        b = int(25 + ratio * 18)
        pygame.draw.line(bg, (r, g, b), (0, y), (1280, y))

    # Константы layout
    LIST_X    = 20
    LIST_Y    = 80
    LIST_W    = 280
    LIST_ITEM = 46          # высота строки
    VISIBLE   = 13          # видимых строк в списке
    PREV_X    = 320         # X начала панели превью
    PREV_Y    = 60
    PREV_W    = 940
    PREV_H    = 630

    scroll_offset = 0       # для прокрутки списка

    running = True
    while running:
        dt       = clock.tick(60) / 1000.0
        time_acc += dt

        # ── События ──────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(characters)
                    # Прокрутка
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + VISIBLE:
                        scroll_offset = selected - VISIBLE + 1

                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(characters)
                    if selected < scroll_offset:
                        scroll_offset = 0
                    elif selected >= scroll_offset + VISIBLE:
                        scroll_offset = selected - VISIBLE + 1

            if event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y
                scroll_offset = max(0, min(scroll_offset,
                                          max(0, len(characters) - VISIBLE)))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for vis_i in range(VISIBLE):
                    real_i = scroll_offset + vis_i
                    if real_i >= len(characters):
                        break
                    item_rect = pygame.Rect(
                        LIST_X, LIST_Y + vis_i * LIST_ITEM,
                        LIST_W, LIST_ITEM - 4
                    )
                    if item_rect.collidepoint(event.pos):
                        selected = real_i
                        break

        # ── Рисуем фон ───────────────────────────────────────────────
        screen.blit(bg, (0, 0))

        # ── Заголовок ────────────────────────────────────────────────
        title_s = font_title.render("Галерея персонажей", True, COLOR_PRIMARY_LIGHT)
        screen.blit(title_s, (LIST_X, 28))

        count_s = font_small.render(
            f"{selected + 1} / {len(characters)}", True, COLOR_TEXT_DIM)
        screen.blit(count_s, (LIST_X + LIST_W - count_s.get_width(), 32))

        # ── Панель списка ─────────────────────────────────────────────
        list_bg = pygame.Surface((LIST_W + 10, VISIBLE * LIST_ITEM + 16),
                                  pygame.SRCALPHA)
        pygame.draw.rect(list_bg, (18, 15, 28, 210),
                         list_bg.get_rect(), border_radius=10)
        pygame.draw.rect(list_bg, (*COLOR_PRIMARY_DARK, 130),
                         list_bg.get_rect(), width=1, border_radius=10)
        screen.blit(list_bg, (LIST_X - 5, LIST_Y - 8))

        for vis_i in range(VISIBLE):
            real_i = scroll_offset + vis_i
            if real_i >= len(characters):
                break

            char    = characters[real_i]
            is_sel  = (real_i == selected)
            iy      = LIST_Y + vis_i * LIST_ITEM

            # Фон строки
            row_surf = pygame.Surface((LIST_W, LIST_ITEM - 4), pygame.SRCALPHA)
            if is_sel:
                pygame.draw.rect(row_surf, (*COLOR_ACCENT[:3], 45),
                                 row_surf.get_rect(), border_radius=6)
                pygame.draw.rect(row_surf, (*COLOR_ACCENT[:3], 200),
                                 row_surf.get_rect(), width=2, border_radius=6)
            else:
                pygame.draw.rect(row_surf, (30, 26, 44, 160),
                                 row_surf.get_rect(), border_radius=6)
            screen.blit(row_surf, (LIST_X, iy))

            # Номер
            num_s = font_tiny.render(f"{real_i + 1}.", True, COLOR_TEXT_DIM)
            screen.blit(num_s, (LIST_X + 6, iy + 6))

            # Имя
            name_color = COLOR_ACCENT if is_sel else COLOR_TEXT
            name_s = font_normal.render(char["name"], True, name_color)
            screen.blit(name_s, (LIST_X + 30, iy + 4))

            # Роль
            role_s = font_tiny.render(char["role"], True, COLOR_TEXT_DIM)
            screen.blit(role_s, (LIST_X + 30, iy + 23))

        # Скроллбар
        if len(characters) > VISIBLE:
            sb_h   = VISIBLE * LIST_ITEM
            th     = max(20, int(sb_h * VISIBLE / len(characters)))
            ty_off = int((sb_h - th) * scroll_offset /
                         max(1, len(characters) - VISIBLE))
            pygame.draw.rect(screen, (40, 35, 55),
                             (LIST_X + LIST_W + 2, LIST_Y, 4, sb_h), border_radius=2)
            pygame.draw.rect(screen, COLOR_PRIMARY_DARK,
                             (LIST_X + LIST_W + 2, LIST_Y + ty_off, 4, th),
                             border_radius=2)

        # ── Панель превью ─────────────────────────────────────────────
        pp = pygame.Surface((PREV_W, PREV_H), pygame.SRCALPHA)
        pygame.draw.rect(pp, (18, 15, 28, 225),
                         pp.get_rect(), border_radius=14)
        pygame.draw.rect(pp, (*COLOR_PRIMARY_DARK, 150),
                         pp.get_rect(), width=1, border_radius=14)
        screen.blit(pp, (PREV_X, PREV_Y))

        char_data = characters[selected]
        obj       = char_data["obj"]
        is_player = char_data["is_player"]

        # Имя + роль
        cname_s = font_title.render(char_data["name"], True, COLOR_ACCENT)
        screen.blit(cname_s, (PREV_X + 30, PREV_Y + 22))

        role_label = font_normal.render(
            char_data["role"], True, COLOR_TEXT_DIM)
        screen.blit(role_label, (PREV_X + 30, PREV_Y + 56))

        # Описание
        desc_lines = wrap_text(char_data["description"], font_normal, PREV_W - 80)
        desc_y = PREV_Y + 80
        for line in desc_lines[:3]:
            ls = font_normal.render(line, True, COLOR_TEXT)
            screen.blit(ls, (PREV_X + 30, desc_y))
            desc_y += 20

        # ── Большое превью (центр) ────────────────────────────────────
        big_size  = 130
        big_scale = 3.2
        big_surf  = draw_character_to_surface(
            obj, is_player, "down", time_acc, big_size)

        scaled_w  = int(big_size * big_scale)
        scaled_h  = int(big_size * big_scale)
        big_scaled = pygame.transform.scale(big_surf, (scaled_w, scaled_h))

        # Зона превью
        zone_cx = PREV_X + PREV_W // 2
        zone_cy = PREV_Y + 340
        zone_r  = 110

        # Тень-круг под персонажем
        shadow_surf = pygame.Surface((zone_r * 2 + 20, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60),
                            (0, 0, zone_r * 2 + 20, 40))
        screen.blit(shadow_surf, (zone_cx - zone_r - 10, zone_cy + zone_r - 10))

        # «Пьедестал»
        ped_surf = pygame.Surface((zone_r * 2 + 20, zone_r * 2 + 20),
                                   pygame.SRCALPHA)
        pygame.draw.circle(ped_surf, (30, 26, 44, 160),
                           (zone_r + 10, zone_r + 10), zone_r)
        pygame.draw.circle(ped_surf, (*COLOR_PRIMARY_DARK, 120),
                           (zone_r + 10, zone_r + 10), zone_r, width=2)
        screen.blit(ped_surf, (zone_cx - zone_r - 10, zone_cy - zone_r - 10))

        # Сам персонаж
        screen.blit(big_scaled,
                    (zone_cx - scaled_w // 2,
                     zone_cy - scaled_h // 2 + 20))

        # ── Направления (маленькие) ───────────────────────────────────
        dir_label_s = font_small.render("Все направления:", True, COLOR_TEXT_DIM)
        screen.blit(dir_label_s, (PREV_X + 30, PREV_Y + 490))

        small_size  = 60
        small_scale = 1.6
        dir_start_x = PREV_X + 30

        for di, direction in enumerate(DIRECTIONS):
            ds = draw_character_to_surface(
                obj, is_player, direction, time_acc, small_size)
            ds_scaled = pygame.transform.scale(
                ds, (int(small_size * small_scale),
                     int(small_size * small_scale)))

            dx_pos = dir_start_x + di * (int(small_size * small_scale) + 12)
            dy_pos = PREV_Y + 510

            # Рамка
            frame = pygame.Surface(
                (int(small_size * small_scale) + 4,
                 int(small_size * small_scale) + 4), pygame.SRCALPHA)
            pygame.draw.rect(frame, (30, 26, 44, 180),
                             frame.get_rect(), border_radius=6)
            screen.blit(frame, (dx_pos - 2, dy_pos - 2))

            screen.blit(ds_scaled, (dx_pos, dy_pos))

            dir_name_s = font_tiny.render(direction, True, COLOR_TEXT_DIM)
            screen.blit(dir_name_s,
                        (dx_pos + int(small_size * small_scale) // 2
                         - dir_name_s.get_width() // 2,
                         dy_pos + int(small_size * small_scale) + 2))

        # ── Параметры внешности (NPC) ─────────────────────────────────
        if not is_player and hasattr(obj, "appearance"):
            a = obj.appearance

            info_x = PREV_X + PREV_W // 2 + 60
            info_y = PREV_Y + 150

            info_bg = pygame.Surface((360, 300), pygame.SRCALPHA)
            pygame.draw.rect(info_bg, (25, 22, 38, 200),
                             info_bg.get_rect(), border_radius=10)
            pygame.draw.rect(info_bg, (*COLOR_PRIMARY_DARK, 100),
                             info_bg.get_rect(), width=1, border_radius=10)
            screen.blit(info_bg, (info_x, info_y))

            inf_label = font_heading.render(
                "Параметры", True, COLOR_PRIMARY_LIGHT)
            screen.blit(inf_label, (info_x + 14, info_y + 12))

            def color_box(surface, x, y, color, size=14):
                pygame.draw.rect(surface, color, (x, y, size, size),
                                 border_radius=3)
                pygame.draw.rect(surface, (255, 255, 255, 60),
                                 (x, y, size, size), width=1, border_radius=3)

            params = [
                ("Причёска",     a.hair_style,                    None),
                ("Борода",       "Да" if a.has_beard else "Нет",  None),
                ("Шляпа",        "Да" if a.has_hat   else "Нет",  None),
                ("Аксессуар",    a.accessory or "Нет",            None),
                ("Роль",         obj.role,                        None),
                ("Реплик",       str(len(obj.dialogues)),         None),
            ]

            color_params = [
                ("Тело",     a.body_color),
                ("Кожа",     a.skin_color),
                ("Волосы",   a.hair_color),
                ("Одежда",   a.outfit_color),
            ]

            py_off = info_y + 40
            for pname, pval, _ in params:
                pn_s = font_small.render(f"{pname}:", True, COLOR_TEXT_DIM)
                pv_s = font_small.render(str(pval),   True, COLOR_TEXT)
                screen.blit(pn_s, (info_x + 14, py_off))
                screen.blit(pv_s, (info_x + 110, py_off))
                py_off += 20

            py_off += 8
            cp_label = font_small.render("Цвета:", True, COLOR_TEXT_DIM)
            screen.blit(cp_label, (info_x + 14, py_off))
            py_off += 20

            for cpname, cpcolor in color_params:
                color_box(screen, info_x + 14, py_off, cpcolor)
                cn_s = font_small.render(cpname, True, COLOR_TEXT_DIM)
                screen.blit(cn_s, (info_x + 34, py_off))

                rgb_s = font_tiny.render(
                    f"rgb{cpcolor}", True, COLOR_TEXT_DIM)
                screen.blit(rgb_s, (info_x + 110, py_off + 2))
                py_off += 22

        # ── Диалоги персонажа ─────────────────────────────────────────
        if not is_player and obj.dialogues:
            dlg_x = PREV_X + PREV_W // 2 + 60
            dlg_y = PREV_Y + 460

            dlg_bg = pygame.Surface((360, 155), pygame.SRCALPHA)
            pygame.draw.rect(dlg_bg, (25, 22, 38, 200),
                             dlg_bg.get_rect(), border_radius=10)
            pygame.draw.rect(dlg_bg, (*COLOR_PRIMARY_DARK, 100),
                             dlg_bg.get_rect(), width=1, border_radius=10)
            screen.blit(dlg_bg, (dlg_x, dlg_y))

            dlg_label = font_heading.render(
                "Реплики:", True, COLOR_PRIMARY_LIGHT)
            screen.blit(dlg_label, (dlg_x + 14, dlg_y + 12))

            max_dlg = min(len(obj.dialogues), 3)
            dy_off  = dlg_y + 36

            for di in range(max_dlg):
                raw  = obj.dialogues[di]["text"]
                w_lines = wrap_text(raw, font_tiny, 320)
                for wl in w_lines[:2]:
                    wl_s = font_tiny.render(
                        ("  " if wl == w_lines[0] else "    ") + wl,
                        True, COLOR_TEXT_DIM)
                    screen.blit(wl_s, (dlg_x + 14, dy_off))
                    dy_off += 16
                dy_off += 4

        # ── Подсказки управления ──────────────────────────────────────
        controls = (
            "↑ ↓  /  колёсико  /  клик — выбор      ESC — выход"
        )
        ctrl_s = font_small.render(controls, True, COLOR_TEXT_DIM)
        screen.blit(ctrl_s, (640 - ctrl_s.get_width() // 2, 700))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()