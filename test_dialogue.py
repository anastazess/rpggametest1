"""
Тест: диалоговая система.
Запуск: python test_dialogue.py
"""

import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.world.dialogue import DialogueBox
from game.ui.notifications import NotificationManager


# -------------------------------------------------------
# Наборы диалогов для тестирования
# -------------------------------------------------------
DIALOGUES = {

    "intro": {
        "name": "Вступление в игру",
        "color": (100, 150, 220),
        "lines": [
            {"speaker": "???",
             "text": "Эй, очнись! Ты в порядке?",
             "portrait_color": (100, 150, 200)},
            {"speaker": "Странник",
             "text": "Мы нашли тебя без сознания у городских ворот. "
                     "Ты помнишь, что произошло?",
             "portrait_color": (100, 150, 200)},
            {"speaker": "Вы",
             "text": "Я... не помню. Где я?",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Странник",
             "text": "Это Валенхольм — последний оплот людей в этих землях. "
                     "После Падения мир изменился навсегда...",
             "portrait_color": (100, 150, 200)},
            {"speaker": "Странник",
             "text": "Если тебе некуда идти, загляни в Гильдию Искателей. "
                     "Они всегда ищут новых рекрутов.",
             "portrait_color": (100, 150, 200)},
            {"speaker": "Вы",
             "text": "Спасибо. Я разберусь.",
             "portrait_color": (180, 140, 255)},
        ],
    },

    "guild": {
        "name": "Гильдия Искателей",
        "color": (200, 150, 100),
        "lines": [
            {"speaker": "Регистратор",
             "text": "Добро пожаловать в Гильдию Искателей! "
                     "Я вижу, ты новенький.",
             "portrait_color": (200, 150, 100)},
            {"speaker": "Регистратор",
             "text": "Мы занимаемся исследованием руин, охотой на монстров "
                     "и поиском артефактов Древних. Работа опасная, но оплата щедрая.",
             "portrait_color": (200, 150, 100)},
            {"speaker": "Вы",
             "text": "Звучит интересно. Как вступить?",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Регистратор",
             "text": "Для начала нужно выполнить одно пробное задание. "
                     "Это просто — сходи в Туманный лес и принеси мне "
                     "три синих гриба. Они светятся в темноте, не ошибёшься.",
             "portrait_color": (200, 150, 100)},
            {"speaker": "Вы",
             "text": "Принято. Я скоро вернусь.",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Регистратор",
             "text": "Удачи. И будь осторожен — в лесу водятся теневые волки.",
             "portrait_color": (200, 150, 100)},
        ],
    },

    "merchant": {
        "name": "Торговец",
        "color": (100, 200, 100),
        "lines": [
            {"speaker": "Торговец Браен",
             "text": "Добро пожаловать в мою лавку, путник! "
                     "У меня найдётся всё, что нужно настоящему герою.",
             "portrait_color": (100, 200, 100)},
            {"speaker": "Вы",
             "text": "Что у тебя есть на продажу?",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Торговец Браен",
             "text": "Зелья здоровья, магические свитки, отличное оружие! "
                     "Сегодня особая скидка на зелья — 20%, не упусти!",
             "portrait_color": (100, 200, 100)},
            {"speaker": "Вы",
             "text": "Интересно, но сейчас у меня маловато монет.",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Торговец Браен",
             "text": "Понимаю. Заходи когда разбогатеешь — "
                     "мои цены лучшие в Валенхольме!",
             "portrait_color": (100, 200, 100)},
        ],
    },

    "old_man": {
        "name": "Старый мудрец",
        "color": (180, 160, 220),
        "lines": [
            {"speaker": "Мудрец Аэлрон",
             "text": "А, молодой путник... Я ждал тебя. "
                     "Звёзды предрекли твоё появление ещё три луны назад.",
             "portrait_color": (180, 160, 220)},
            {"speaker": "Вы",
             "text": "Вы меня знаете? Мы раньше встречались?",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Мудрец Аэлрон",
             "text": "Нет. Но Тьма знает тебя. "
                     "То, что ты ищешь — Осколок Рассвета — "
                     "существует. Но цена велика.",
             "portrait_color": (180, 160, 220)},
            {"speaker": "Вы",
             "text": "Откуда вы знаете, что я ищу?",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Мудрец Аэлрон",
             "text": "Потому что все, кто приходит из-за Завесы, "
                     "ищут одно и то же. Ответы на вопросы, "
                     "которые они боятся задать вслух.",
             "portrait_color": (180, 160, 220)},
            {"speaker": "Мудрец Аэлрон",
             "text": "Найди три Хранителя Памяти. "
                     "Они укажут тебе путь. "
                     "Начни с того, кто живёт в тени башни.",
             "portrait_color": (180, 160, 220)},
            {"speaker": "Вы",
             "text": "Подождите — что такое Завеса?",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Мудрец Аэлрон",
             "text": "...",
             "portrait_color": (180, 160, 220)},
        ],
    },

    "enemy": {
        "name": "Враждебный бандит",
        "color": (220, 80, 80),
        "lines": [
            {"speaker": "Бандит",
             "text": "Стой! Кошелёк или жизнь, чужеземец.",
             "portrait_color": (200, 80, 60)},
            {"speaker": "Вы",
             "text": "Ты выбрал не ту цель.",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Бандит",
             "text": "Смелые слова для того, кто стоит один "
                     "против пятерых моих людей. "
                     "Последний шанс, герой.",
             "portrait_color": (200, 80, 60)},
            {"speaker": "Вы",
             "text": "Твои люди уже убегают.",
             "portrait_color": (180, 140, 255)},
            {"speaker": "Бандит",
             "text": "...Что?! Трусы! "
                     "Ладно, ты мне нравишься. "
                     "Убирайся, пока я добрый.",
             "portrait_color": (200, 80, 60)},
        ],
    },
}


def main():
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Тест диалогов — Echoes of the Fallen")

    clock         = pygame.time.Clock()
    dialogue      = DialogueBox(screen)
    notifications = NotificationManager(screen)

    font_title  = pygame.font.SysFont("georgia",  28, bold=True)
    font_sub    = pygame.font.SysFont("segoeui",  18)
    font_small  = pygame.font.SysFont("segoeui",  15)
    font_hint   = pygame.font.SysFont("segoeui",  13)

    dialogue_keys = list(DIALOGUES.keys())
    selected = 0
    time_acc = 0.0

    # Простой фоновый «город»
    bg = pygame.Surface((1280, 720))
    for y in range(720):
        ratio = y / 720
        r = int(30 + ratio * 20)
        g = int(50 + ratio * 30)
        b = int(25 + ratio * 15)
        pygame.draw.line(bg, (r, g, b), (0, y), (1280, y))

    # Несколько домиков для атмосферы
    for bx, bw in [(100, 80), (250, 100), (500, 90),
                   (700, 110), (950, 85), (1100, 95)]:
        h = 80 + (bx % 3) * 20
        by = 400 - h
        pygame.draw.rect(bg, (60, 50, 70), (bx, by, bw, h))
        pts = [(bx - 10, by + 5), (bx + bw // 2, by - 30),
               (bx + bw + 10, by + 5)]
        pygame.draw.polygon(bg, (100, 50, 50), pts)

    # Земля
    pygame.draw.rect(bg, (55, 90, 40), (0, 400, 1280, 320))

    def draw_selector():
        """Панель выбора диалога."""
        panel_w = 340
        panel_h = len(DIALOGUES) * 58 + 70
        panel_x = 1280 // 2 - panel_w // 2
        panel_y = 720  // 2 - panel_h // 2

        surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (18, 15, 28, 230),
                         (0, 0, panel_w, panel_h), border_radius=14)
        pygame.draw.rect(surf, (*COLOR_PRIMARY_DARK, 160),
                         (0, 0, panel_w, panel_h), width=2, border_radius=14)
        screen.blit(surf, (panel_x, panel_y))

        title_s = font_title.render("Выбор диалога", True, COLOR_PRIMARY_LIGHT)
        screen.blit(title_s, (panel_x + panel_w // 2 - title_s.get_width() // 2,
                               panel_y + 16))

        for i, key in enumerate(dialogue_keys):
            data  = DIALOGUES[key]
            is_sel = (i == selected)

            item_y = panel_y + 60 + i * 58
            item_w = panel_w - 40

            # Фон элемента
            item_surf = pygame.Surface((item_w, 48), pygame.SRCALPHA)
            if is_sel:
                pygame.draw.rect(item_surf, (*data["color"], 50),
                                 (0, 0, item_w, 48), border_radius=8)
                pygame.draw.rect(item_surf, (*data["color"], 200),
                                 (0, 0, item_w, 48), width=2, border_radius=8)
            else:
                pygame.draw.rect(item_surf, (30, 26, 45, 180),
                                 (0, 0, item_w, 48), border_radius=8)
                pygame.draw.rect(item_surf, (60, 50, 80, 120),
                                 (0, 0, item_w, 48), width=1, border_radius=8)
            screen.blit(item_surf, (panel_x + 20, item_y))

            # Номер клавиши
            key_text = f"[{i + 1}]"
            key_col  = data["color"] if is_sel else COLOR_TEXT_DIM
            key_s = font_sub.render(key_text, True, key_col)
            screen.blit(key_s, (panel_x + 30, item_y + 5))

            # Название
            name_col = COLOR_TEXT if is_sel else COLOR_TEXT_DIM
            name_s = font_small.render(data["name"], True, name_col)
            screen.blit(name_s, (panel_x + 70, item_y + 4))

            # Кол-во реплик
            count_text = f"{len(data['lines'])} реплик"
            count_s = font_hint.render(count_text, True, COLOR_TEXT_DIM)
            screen.blit(count_s, (panel_x + 70, item_y + 26))

        # Подсказка
        hint_text = "1–5: выбор   ENTER/E: запустить   ESC: выход"
        hint_s = font_hint.render(hint_text, True, COLOR_TEXT_DIM)
        screen.blit(hint_s, (panel_x + panel_w // 2 - hint_s.get_width() // 2,
                              panel_y + panel_h - 22))

    def draw_replay_hint():
        """Подсказка когда диалог завершён."""
        text = "Диалог завершён  |  ENTER — начать снова  |  ESC — вернуться к выбору"
        sw = screen.get_width()
        sh = screen.get_height()
        s = font_hint.render(text, True, COLOR_TEXT_DIM)
        bgr = pygame.Surface((s.get_width() + 24, 26), pygame.SRCALPHA)
        pygame.draw.rect(bgr, (18, 15, 28, 200), bgr.get_rect(), border_radius=6)
        screen.blit(bgr, (sw // 2 - bgr.get_width() // 2, sh - 170))
        screen.blit(s,   (sw // 2 - s.get_width()   // 2, sh - 166))

    mode = "select"   # "select" | "dialogue" | "done"

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        time_acc += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if mode == "select":
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Цифровые клавиши 1–5
                    for i, _ in enumerate(dialogue_keys):
                        if event.key == getattr(pygame, f"K_{i + 1}", None):
                            selected = i

                    # Стрелки
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(dialogue_keys)
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(dialogue_keys)

                    # Запуск диалога
                    if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                        key  = dialogue_keys[selected]
                        data = DIALOGUES[key]
                        dialogue.start_dialogue(data["lines"])
                        notifications.show_info(
                            f"Начат диалог: {data['name']}",
                            title="Диалог"
                        )
                        mode = "dialogue"

                elif mode == "dialogue":
                    # ESC из диалога — возврат к выбору
                    if event.key == pygame.K_ESCAPE:
                        dialogue.active = False
                        mode = "select"
                    else:
                        if dialogue.handle_event(event):
                            if not dialogue.active:
                                mode = "done"
                                notifications.show_success(
                                    f"Диалог «{DIALOGUES[dialogue_keys[selected]]['name']}» завершён"
                                )

                elif mode == "done":
                    if event.key == pygame.K_ESCAPE:
                        mode = "select"
                    if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                        key  = dialogue_keys[selected]
                        data = DIALOGUES[key]
                        dialogue.start_dialogue(data["lines"])
                        mode = "dialogue"

            # Клик по диалогу
            if mode == "dialogue" and event.type == pygame.MOUSEBUTTONDOWN:
                if dialogue.handle_event(event):
                    if not dialogue.active:
                        mode = "done"

        # Обновление
        dialogue.update(dt)
        notifications.update(dt)

        # Отрисовка
        screen.blit(bg, (0, 0))

        if mode == "select":
            draw_selector()
        elif mode == "dialogue":
            dialogue.draw()
        elif mode == "done":
            draw_replay_hint()
            dialogue.draw()

        notifications.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()