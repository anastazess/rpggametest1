import pygame
from game.constants import *
from game.world.player import Player
from game.world.game_map import GameMap, PLAYER_SPAWN_X, PLAYER_SPAWN_Y
from game.world.dialogue import DialogueBox
from game.world.interiors import get_interior
from game.ui.notifications import NotificationManager
from game.menu.icons import Icons
from game.player.inventory import Inventory, get_item
from game.player.player_stats import PlayerStats
from game.ui.inventory_ui import InventoryUI
from game.save_system import SaveData, autosave, load_game, has_autosave


class GameWorld:
    """Основной игровой мир."""

    INTRO_DIALOGUE = [
        {"speaker": "???",
         "role": "",
         "text": "Эй, очнись! Ты в порядке?",
         "portrait_color": (100, 150, 200)},
        {"speaker": "Странник",
         "role": "Путешественник",
         "text": "Мы нашли тебя без сознания у городских ворот. Ты помнишь, что произошло?",
         "portrait_color": (100, 150, 200)},
        {"speaker": "Герой",
         "role": "",
         "text": "Я... не помню. Где я?",
         "portrait_color": (180, 200, 255)},
        {"speaker": "Странник",
         "role": "Путешественник",
         "text": "Это Валенхольм — последний оплот людей в этих землях. После Падения мир изменился навсегда...",
         "portrait_color": (100, 150, 200)},
        {"speaker": "Странник",
         "role": "Путешественник",
         "text": "Если тебе некуда идти, загляни в Гильдию Искателей. Они всегда ищут новых рекрутов.",
         "portrait_color": (100, 150, 200)},
        {"speaker": "Герой",
         "role": "",
         "text": "Спасибо. Я разберусь.",
         "portrait_color": (180, 200, 255)},
    ]

    # Автосохранение каждые N секунд
    AUTOSAVE_INTERVAL = 60.0

    def __init__(self, screen, settings_manager, load_save=False):
        self.screen = screen
        self.settings_manager = settings_manager
        self.settings = settings_manager.settings
        self.clock = pygame.time.Clock()

        self.state = "intro"       # intro | exploring | interior
        self.running = True
        self.intro_complete = False
        self.game_time = 0.0
        self.autosave_timer = 0.0

        # Данные игрока
        self.player_stats = PlayerStats()
        self.inventory    = Inventory()

        # Загрузка сохранения
        if load_save and has_autosave():
            save_data = load_game()
            if save_data:
                self.player_stats  = save_data.player_stats
                self.inventory     = save_data.inventory
                self.game_time     = save_data.game_time
                self.intro_complete = True
                self.state          = "exploring"

        # Стартовые предметы (только новая игра)
        if not load_save:
            self.inventory.add_item(get_item("wooden_sword"),   1)
            self.inventory.add_item(get_item("leather_armor"),  1)
            self.inventory.add_item(get_item("leather_boots"),  1)
            self.inventory.add_item(get_item("health_potion"),  3)
            self.inventory.add_item(get_item("old_letter"),     1)

        # Камера
        self.camera_x = 0.0
        self.camera_y = 0.0

        # Компоненты
        self.game_map      = GameMap()
        self.player = Player(PLAYER_SPAWN_X, PLAYER_SPAWN_Y)
        self.dialogue      = DialogueBox(screen)
        self.notifications = NotificationManager(screen)
        self.inventory_ui  = InventoryUI(screen, self.player_stats, self.inventory)

        # Интерьер
        self.current_interior    = None
        self.interior_camera_x   = 0.0
        self.interior_camera_y   = 0.0
        self.interior_player_pos = (0, 0)   # позиция перед входом

        # UI
        self.font_ui       = pygame.font.SysFont("segoeui", 16)
        self.font_location = pygame.font.SysFont("segoeui", 14)
        self.font_debug    = pygame.font.SysFont("segoeui", 13)

        self.show_debug = False

        if not self.intro_complete:
            self.dialogue.start_dialogue(self.INTRO_DIALOGUE)

    # ------------------------------------------------------------------
    # Сохранение
    # ------------------------------------------------------------------

    def _make_save_data(self) -> SaveData:
        sd = SaveData()
        sd.player_stats = self.player_stats
        sd.inventory    = self.inventory
        sd.position     = (self.player.x, self.player.y)
        sd.game_time    = self.game_time
        sd.current_location = (
            self.current_interior.name
            if self.current_interior else "world"
        )
        return sd

    def _do_autosave(self):
        ok = autosave(self._make_save_data())
        if ok:
            self.notifications.show_success("Игра автоматически сохранена")

    # ------------------------------------------------------------------
    # Камера
    # ------------------------------------------------------------------

    def _update_camera_world(self):
        sw, sh = self.screen.get_size()
        tx = self.player.x - sw // 2 + self.player.width  // 2
        ty = self.player.y - sh // 2 + self.player.height // 2
        self.camera_x += (tx - self.camera_x) * 0.12
        self.camera_y += (ty - self.camera_y) * 0.12
        self.camera_x = max(0, min(self.camera_x,
                                   self.game_map.width  - sw))
        self.camera_y = max(0, min(self.camera_y,
                                   self.game_map.height - sh))

    def _update_camera_interior(self):
        sw, sh = self.screen.get_size()
        interior = self.current_interior
        tx = self.player.x - sw // 2 + self.player.width  // 2
        ty = self.player.y - sh // 2 + self.player.height // 2
        self.interior_camera_x += (tx - self.interior_camera_x) * 0.12
        self.interior_camera_y += (ty - self.interior_camera_y) * 0.12
        self.interior_camera_x = max(0, min(self.interior_camera_x,
                                            max(0, interior.width  - sw)))
        self.interior_camera_y = max(0, min(self.interior_camera_y,
                                            max(0, interior.height - sh)))

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def _draw_hud_world(self):
        sw, sh = self.screen.get_size()

        # Название локации
        loc_text = "Валенхольм"
        if self.current_interior:
            loc_text = self.current_interior.name
        loc_surf = self.font_location.render(loc_text, True, COLOR_TEXT_DIM)
        loc_bg = pygame.Surface((loc_surf.get_width() + 20, 24), pygame.SRCALPHA)
        pygame.draw.rect(loc_bg, (18, 15, 28, 180), loc_bg.get_rect(), border_radius=5)
        self.screen.blit(loc_bg,  (15, 15))
        self.screen.blit(loc_surf, (25, 19))

        # Мини-карта (только снаружи)
        if self.state == "exploring":
            self._draw_minimap()

        # HP / MP бары
        self._draw_vitals(sw, sh)

        # Подсказки внизу
        hints = [
            "WASD — движение",
            "E — взаимодействие",
            "I — инвентарь",
            "ESC — меню",
        ]
        if self.current_interior:
            hints.append("SHIFT+E — выйти из здания")

        hint_text = "  |  ".join(hints)
        hint_surf = self.font_ui.render(hint_text, True, COLOR_TEXT_DIM)
        hbg = pygame.Surface((hint_surf.get_width() + 20, 26), pygame.SRCALPHA)
        pygame.draw.rect(hbg, (18, 15, 28, 150), hbg.get_rect(), border_radius=5)
        self.screen.blit(hbg, (sw // 2 - hbg.get_width() // 2, sh - 40))
        self.screen.blit(hint_surf, (sw // 2 - hint_surf.get_width() // 2, sh - 36))

    def _draw_vitals(self, sw, sh):
        bx = 15
        by = sh - 90
        bar_w = 160
        bar_h = 18

        stats = self.player_stats

        # HP
        hp_ratio = stats.current_hp / max(1, stats.max_hp)
        pygame.draw.rect(self.screen, (80, 25, 25),
                         (bx, by, bar_w, bar_h), border_radius=4)
        if hp_ratio > 0:
            pygame.draw.rect(self.screen, (210, 55, 55),
                             (bx, by, int(bar_w * hp_ratio), bar_h), border_radius=4)
        hp_text = f"HP  {stats.current_hp}/{stats.max_hp}"
        hp_surf = self.font_location.render(hp_text, True, COLOR_TEXT)
        self.screen.blit(hp_surf, (bx + 6, by + 1))

        # MP
        mp_ratio = stats.current_mp / max(1, stats.max_mp)
        pygame.draw.rect(self.screen, (25, 35, 90),
                         (bx, by + 24, bar_w, bar_h), border_radius=4)
        if mp_ratio > 0:
            pygame.draw.rect(self.screen, (55, 90, 210),
                             (bx, by + 24, int(bar_w * mp_ratio), bar_h), border_radius=4)
        mp_text = f"MP  {stats.current_mp}/{stats.max_mp}"
        mp_surf = self.font_location.render(mp_text, True, COLOR_TEXT)
        self.screen.blit(mp_surf, (bx + 6, by + 25))

        # Золото
        gold_surf = self.font_location.render(
            f"Золото: {self.inventory.gold}", True, COLOR_ACCENT)
        self.screen.blit(gold_surf, (bx, by + 50))

        # Уровень
        lvl_surf = self.font_location.render(
            f"Ур. {self.player_stats.level}", True, COLOR_PRIMARY_LIGHT)
        self.screen.blit(lvl_surf, (bx + bar_w + 10, by))

    def _draw_minimap(self):
        sw, _ = self.screen.get_size()
        mw, mh = 170, 115
        mx, my = sw - mw - 15, 15

        mm = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.rect(mm, (18, 15, 28, 210), (0, 0, mw, mh), border_radius=8)
        pygame.draw.rect(mm, (*COLOR_PRIMARY_DARK, 160), (0, 0, mw, mh),
                         width=1, border_radius=8)

        sx = (mw - 10) / self.game_map.width
        sy = (mh - 10) / self.game_map.height

        for road in self.game_map.roads:
            pygame.draw.rect(mm, (70, 60, 50),
                             (5 + int(road.x * sx), 5 + int(road.y * sy),
                              max(2, int(road.width  * sx)),
                              max(2, int(road.height * sy))))

        for b in self.game_map.buildings:
            bx_ = 5 + int(b.x * sx)
            by_ = 5 + int(b.y * sy)
            bw  = max(3, int(b.width  * sx))
            bh  = max(3, int(b.height * sy))
            pygame.draw.rect(mm, (160, 110, 80), (bx_, by_, bw, bh))

        px_ = 5 + int(self.player.x * sx)
        py_ = 5 + int(self.player.y * sy)
        pygame.draw.circle(mm, COLOR_ACCENT, (px_, py_), 3)

        self.screen.blit(mm, (mx, my))

        cap = self.font_debug.render("Карта", True, COLOR_TEXT_DIM)
        self.screen.blit(cap, (mx + mw // 2 - cap.get_width() // 2, my + mh + 3))

    def _draw_debug(self):
        if not self.show_debug:
            return
        lines = [
            f"Позиция: ({int(self.player.x)}, {int(self.player.y)})",
            f"Камера:  ({int(self.camera_x)}, {int(self.camera_y)})",
            f"Состояние: {self.state}",
            f"HP: {self.player_stats.current_hp}/{self.player_stats.max_hp}",
            f"Золото: {self.inventory.gold}",
        ]
        for i, line in enumerate(lines):
            s = self.font_debug.render(line, True, COLOR_TEXT_DIM)
            self.screen.blit(s, (15, 55 + i * 18))

    # ------------------------------------------------------------------
    # Вход / выход из зданий
    # ------------------------------------------------------------------

    def _enter_building(self, building):
        interior = get_interior(building.name)
        if interior is None:
            self.notifications.show_warning("Здание пока недоступно")
            return

        self.current_interior = interior
        self.interior_player_pos = (self.player.x, self.player.y)

        # Ставим игрока у входа
        ep = interior.entry_point
        self.player.x = float(ep[0] - self.player.width  // 2)
        self.player.y = float(ep[1] - self.player.height)

        self.interior_camera_x = 0.0
        self.interior_camera_y = 0.0
        self.state = "interior"

        self.notifications.show_info(
            f"Вы вошли в {interior.name}", title=interior.name
        )

        # Автосохранение при входе
        self._do_autosave()

    def _exit_building(self):
        if self.current_interior is None:
            return

        old_x, old_y = self.interior_player_pos
        self.player.x = float(old_x)
        self.player.y = float(old_y + 20)

        self.current_interior = None
        self.state = "exploring"
        self.notifications.show_info("Вы вышли на улицу")

    # ------------------------------------------------------------------
    # Взаимодействие
    # ------------------------------------------------------------------

    def _interact_world(self):
        """Взаимодействие снаружи: здания или уличные NPC."""
        # Сначала NPC
        npc = self.game_map.get_hovered_npc()
        if npc:
            if npc.dialogues:
                self.dialogue.start_dialogue(npc.get_dialogues())
            return

        # Затем здания
        building = self.game_map.get_hovered_building()
        if building:
            self._enter_building(building)

    def _interact_interior(self):
        """Взаимодействие внутри здания."""
        npc = self.current_interior.get_hovered_npc()
        if npc and npc.dialogues:
            self.dialogue.start_dialogue(npc.get_dialogues())

    # ------------------------------------------------------------------
    # Отрисовка интерьера
    # ------------------------------------------------------------------

    def _draw_interior(self):
        sw, sh = self.screen.get_size()
        interior = self.current_interior
        cx = self.interior_camera_x
        cy = self.interior_camera_y

        # Фон (пол + стены)
        ground = interior.get_ground()
        self.screen.blit(ground, (-cx, -cy))

        # Мебель и NPC (сортировка по Y)
        drawables = []

        for furn in interior.furniture:
            drawables.append((furn.y + furn.height, "furn", furn))

        for npc in interior.npcs:
            drawables.append((npc.y + npc.height, "npc", npc))

        drawables.append((self.player.y + self.player.height, "player", None))

        drawables.sort(key=lambda d: d[0])

        for _, kind, obj in drawables:
            if kind == "furn":
                interior._draw_furniture(self.screen, obj, cx, cy)
            elif kind == "npc":
                obj.draw(self.screen, cx, cy)
            elif kind == "player":
                self.player.draw(self.screen, cx, cy)

        # Рамка вокруг интерьера
        bx = int(-cx)
        by = int(-cy)
        pygame.draw.rect(self.screen, COLOR_PRIMARY_DARK,
                         (bx, by, interior.width, interior.height),
                         width=3, border_radius=0)

        # Затемнение за пределами комнаты
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))

        # Зона над/под/слева/справа
        room_rect = pygame.Rect(bx, by, interior.width, interior.height)
        for dim_rect in [
            pygame.Rect(0, 0, sw, max(0, room_rect.top)),
            pygame.Rect(0, room_rect.bottom, sw, max(0, sh - room_rect.bottom)),
            pygame.Rect(0, 0, max(0, room_rect.left), sh),
            pygame.Rect(room_rect.right, 0, max(0, sw - room_rect.right), sh),
        ]:
            if dim_rect.width > 0 and dim_rect.height > 0:
                pygame.draw.rect(overlay, (0, 0, 0, 200), dim_rect)

        self.screen.blit(overlay, (0, 0))

    def _interact_with_building(self, building):
        if "Гильдию" in building.name:
            self.dialogue.start_dialogue([
                {"speaker": "Селина",
                 "role": "Магистр Гильдии Искателей",
                 "text": "Добро пожаловать в Гильдию Искателей! Я вижу, ты новенький.",
                 "portrait_color": (200, 150, 100)},
                {"speaker": "Селина",
                 "role": "Магистр Гильдии Искателей",
                 "text": "Мы занимаемся исследованием руин, охотой на монстров и поиском артефактов Древних.",
                 "portrait_color": (200, 150, 100)},
                {"speaker": "Селина",
                 "role": "Магистр Гильдии Искателей",
                 "text": "Хочешь вступить? Для начала тебе нужно выполнить пробное задание.",
                 "portrait_color": (200, 150, 100)},
                {"speaker": "Герой",
                 "role": "",
                 "text": "Я готов!",
                 "portrait_color": (180, 200, 255)},
                {"speaker": "Селина",
                 "role": "Магистр Гильдии Искателей",
                 "text": "Отлично! Загляни на доску объявлений — там есть задания для новичков.",
                 "portrait_color": (200, 150, 100)},
            ])
            self.notifications.show_success("Новая локация: Гильдия Искателей")

        elif "Магазин" in building.name:
            self.dialogue.start_dialogue([
                {"speaker": "Браен",
                 "role": "Торговец снаряжением",
                 "text": "Приветствую, путник! У меня лучшие зелья и снаряжение в городе!",
                 "portrait_color": (100, 180, 100)},
                {"speaker": "Браен",
                 "role": "Торговец снаряжением",
                 "text": "К сожалению, магазин пока закрыт на учёт. Загляни позже!",
                 "portrait_color": (100, 180, 100)},
            ])

        elif "Таверну" in building.name:
            self.dialogue.start_dialogue([
                {"speaker": "Олаф",
                 "role": "Хозяин таверны «Пьяный Грифон»",
                 "text": "Добро пожаловать в 'Пьяного Грифона'! Чего желаете?",
                 "portrait_color": (180, 120, 80)},
                {"speaker": "Олаф",
                 "role": "Хозяин таверны «Пьяный Грифон»",
                 "text": "Эль? Горячий ужин? Или, может, комнату на ночь?",
                 "portrait_color": (180, 120, 80)},
                {"speaker": "Герой",
                 "role": "",
                 "text": "Пока просто осмотрюсь, спасибо.",
                 "portrait_color": (180, 200, 255)},
            ])

        elif "Кузницу" in building.name:
            self.dialogue.start_dialogue([
                {"speaker": "Горан",
                 "role": "Мастер-кузнец Валенхольма",
                 "text": "*Удар молота* О, клиент! Подожди минутку...",
                 "portrait_color": (150, 100, 80)},
                {"speaker": "Горан",
                 "role": "Мастер-кузнец Валенхольма",
                 "text": "Так, чего тебе? Оружие? Броня? Ремонт?",
                 "portrait_color": (150, 100, 80)},
                {"speaker": "Герой",
                 "role": "",
                 "text": "Просто смотрю пока.",
                 "portrait_color": (180, 200, 255)},
                {"speaker": "Горан",
                 "role": "Мастер-кузнец Валенхольма",
                 "text": "Ну, когда надумаешь — заходи. Мои клинки лучшие в округе!",
                 "portrait_color": (150, 100, 80)},
            ])

        elif "Храм" in building.name:
            self.dialogue.start_dialogue([
                {"speaker": "Иссара",
                 "role": "Верховная жрица храма Авэлин",
                 "text": "Добро пожаловать в храм Авэлин. Свет богини да пребудет с тобой, путник.",
                 "portrait_color": (200, 170, 230)},
                {"speaker": "Герой",
                 "role": "",
                 "text": "Благодарю. Здесь так спокойно...",
                 "portrait_color": (180, 200, 255)},
                {"speaker": "Иссара",
                 "role": "Верховная жрица храма Авэлин",
                 "text": "Покой — это дар Авэлин. Отдохни столько, сколько нужно.",
                 "portrait_color": (200, 170, 230)},
            ])

    # ------------------------------------------------------------------
    # Основной цикл
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.game_time     += dt
            self.autosave_timer += dt

            # Автосохранение по таймеру
            if self.autosave_timer >= self.AUTOSAVE_INTERVAL:
                self.autosave_timer = 0.0
                if self.state != "intro":
                    self._do_autosave()

            mouse_pos = pygame.mouse.get_pos()

            # ── Обработка событий ──────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._do_autosave()
                    return "quit"

                # Инвентарь перехватывает первым
                if self.inventory_ui.active:
                    if self.inventory_ui.handle_event(event):
                        continue

                # Диалог перехватывает вторым
                if self.dialogue.active:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.dialogue.active = False
                        continue
                    if self.dialogue.handle_event(event):
                        if not self.dialogue.active:
                            # Диалог завершён
                            if not self.intro_complete and self.state == "intro":
                                self.intro_complete = True
                                self.state = "exploring"
                                self.notifications.show_achievement(
                                    "Первые шаги",
                                    "Начните своё приключение",
                                    Icons.draw_sword
                                )
                                self._do_autosave()
                    continue

                if event.type == pygame.KEYDOWN:
                    # ESC
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "interior":
                            self._exit_building()
                        else:
                            self._do_autosave()
                            return "menu"

                    # F1 — debug
                    if event.key == pygame.K_F1:
                        self.show_debug = not self.show_debug

                    # I — инвентарь
                    inv_key = self.settings["keybindings"].get(
                        "inventory", pygame.K_i)
                    if event.key == inv_key:
                        self.inventory_ui.toggle()

                    # E — взаимодействие / выход
                    interact_key = self.settings["keybindings"].get(
                        "interact", pygame.K_e)
                    if event.key == interact_key:
                        if self.state == "interior":
                            keys = pygame.key.get_pressed()
                            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                                self._exit_building()
                            else:
                                self._interact_interior()
                        elif self.state == "exploring":
                            self._interact_world()

            # ── Обновление ─────────────────────────────────────────────
            self.dialogue.update(dt)
            self.notifications.update(dt)
            self.inventory_ui.update(dt, mouse_pos)

            can_move = (
                not self.dialogue.active
                and not self.inventory_ui.active
                and self.state in ("exploring", "interior")
            )

            if can_move:
                keys = pygame.key.get_pressed()
                dx, dy = self.player.handle_input(
                    keys, self.settings["keybindings"])

                if self.state == "exploring":
                    self.player.update(dt, dx, dy, self.game_map.colliders)
                    self.game_map.update(self.player.feet_rect, dt)

                elif self.state == "interior":
                    self.player.update(
                        dt, dx, dy, self.current_interior.colliders)
                    self.current_interior.update(dt, self.player.feet_rect)

                    # Выход через дверь (нижняя граница интерьера)
                    if self.player.y > self.current_interior.height - 20:
                        self._exit_building()

            if self.state == "exploring":
                self._update_camera_world()
            elif self.state == "interior":
                self._update_camera_interior()

            # ── Отрисовка ──────────────────────────────────────────────
            sw, sh = self.screen.get_size()

            if self.state in ("intro", "exploring"):
                self.game_map.draw(
                    self.screen, self.camera_x, self.camera_y, sw, sh)
                self.player.draw(self.screen, self.camera_x, self.camera_y)

            elif self.state == "interior":
                self._draw_interior()

            # HUD (всегда, кроме закрытого инвентаря)
            if not self.inventory_ui.active:
                self._draw_hud_world()

            self._draw_debug()

            # Диалог поверх
            self.dialogue.draw()

            # Инвентарь поверх всего
            self.inventory_ui.draw()

            # Уведомления самыми верхними
            self.notifications.draw()

            pygame.display.flip()

        return "menu"