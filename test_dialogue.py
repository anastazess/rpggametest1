"""
Тест диалогов в стиле Genshin Impact.
Запуск: python test_dialogue.py
"""

import pygame
import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.world.dialogue import DialogueBox


# ── Диалоги ──────────────────────────────────────────────────────────

DIALOGUES = {
    "priestess": {
        "name": "Верховная жрица",
        "lines": [
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "Добро пожаловать в храм Авэлин, богини рассвета, исцеления и вечного света. Мы рады каждому страннику, ищущему покой.",
             "portrait_color": (200, 170, 230)},
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "Авэлин хранит равновесие между светом и тьмой. Без её благословения этот мир давно бы погрузился в хаос и забвение.",
             "portrait_color": (200, 170, 230)},
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "Я чувствую в тебе искру... Ты пришёл из-за Завесы, не так ли? Немногие выживают в том путешествии. Ты — особенный.",
             "portrait_color": (200, 170, 230)},
            {"speaker": "Герой",
             "role": "",
             "text": "Я не помню, как оказался здесь. Всё как в тумане...",
             "portrait_color": (180, 200, 255)},
            {"speaker": "Иссара",
             "role": "Верховная жрица храма Авэлин",
             "text": "Это нормально. Завеса стирает воспоминания. Но они вернутся — когда придёт время. А пока отдохни. Сёстры позаботятся о тебе.",
             "portrait_color": (200, 170, 230)},
        ],
    },
    "guild": {
        "name": "Магистр гильдии",
        "lines": [
            {"speaker": "Селина",
             "role": "Магистр Гильдии Искателей",
             "text": "Ты, должно быть, новый рекрут. Я наблюдала за тобой с момента, как ты вошёл в город. Впечатляющая выносливость для человека без памяти.",
             "portrait_color": (200, 150, 100)},
            {"speaker": "Герой",
             "role": "",
             "text": "Вы знаете обо мне?",
             "portrait_color": (180, 200, 255)},
            {"speaker": "Селина",
             "role": "Магистр Гильдии Искателей",
             "text": "Я знаю обо всём, что происходит в Валенхольме. Это моя работа. Гильдия Искателей — это не просто организация. Это семья, которая защищает город от того, что скрывается во тьме.",
             "portrait_color": (200, 150, 100)},
            {"speaker": "Селина",
             "role": "Магистр Гильдии Искателей",
             "text": "Если хочешь вступить — докажи свою ценность. Принеси мне три синих гриба из Туманного леса. Просто? Не совсем. Там водятся теневые волки.",
             "portrait_color": (200, 150, 100)},
            {"speaker": "Герой",
             "role": "",
             "text": "Я справлюсь. Когда выходить?",
             "portrait_color": (180, 200, 255)},
            {"speaker": "Селина",
             "role": "Магистр Гильдии Искателей",
             "text": "Хм, мне нравится твоя решительность. Отправляйся, когда будешь готов. И помни — возвращайся живым. Мертвые рекруты мне не нужны.",
             "portrait_color": (200, 150, 100)},
        ],
    },
    "blacksmith": {
        "name": "Кузнец",
        "lines": [
            {"speaker": "Горан",
             "role": "Мастер-кузнец Валенхольма",
             "text": "*звон металла* А, клиент! Подожди... Последний удар... Вот! Готово. Чего желаешь, путник?",
             "portrait_color": (150, 100, 80)},
            {"speaker": "Герой",
             "role": "",
             "text": "Мне нужно хорошее оружие.",
             "portrait_color": (180, 200, 255)},
            {"speaker": "Горан",
             "role": "Мастер-кузнец Валенхольма",
             "text": "Хорошее? У меня только лучшее! Каждый клинок я кую три дня и три ночи. Сталь закаляю в ледяной воде горного ручья, а рукоять оборачиваю кожей северного оленя.",
             "portrait_color": (150, 100, 80)},
            {"speaker": "Горан",
             "role": "Мастер-кузнец Валенхольма",
             "text": "Вот что я тебе скажу — принеси мне железной руды, и я выкую тебе такой меч, что даже теневые волки разбегутся от одного его блеска!",
             "portrait_color": (150, 100, 80)},
        ],
    },
    "sage": {
        "name": "Мудрец",
        "lines": [
            {"speaker": "Аэлрон",
             "role": "Хранитель древних знаний",
             "text": "А, молодой путник... Я ждал тебя. Звёзды предрекли твоё появление ещё три луны назад. Садись, нам нужно поговорить.",
             "portrait_color": (180, 160, 220)},
            {"speaker": "Герой",
             "role": "",
             "text": "Откуда вы меня знаете? Я никого здесь не знаю...",
             "portrait_color": (180, 200, 255)},
            {"speaker": "Аэлрон",
             "role": "Хранитель древних знаний",
             "text": "Я не знаю тебя. Но Тьма — знает. И то, что ты ищешь — Осколок Рассвета — существует. Он спрятан там, где свет встречается с тенью.",
             "portrait_color": (180, 160, 220)},
            {"speaker": "Аэлрон",
             "role": "Хранитель древних знаний",
             "text": "Найди три Хранителя Памяти. Они откроют тебе путь. Первый живёт в тени старой башни, что за Туманным лесом. Но будь осторожен — не все хранители дружелюбны.",
             "portrait_color": (180, 160, 220)},
            {"speaker": "Герой",
             "role": "",
             "text": "Что такое Завеса? Почему я ничего не помню?",
             "portrait_color": (180, 200, 255)},
            {"speaker": "Аэлрон",
             "role": "Хранитель древних знаний",
             "text": "Завеса — это граница между мирами. Те, кто проходят сквозь неё, теряют себя. Но иногда... иногда это цена, которую стоит заплатить.",
             "portrait_color": (180, 160, 220)},
            {"speaker": "Аэлрон",
             "role": "Хранитель древних знаний",
             "text": "Не все, кто блуждает — потеряны. Но те, кто пришёл из-за Завесы... никогда не вернутся прежними.",
             "portrait_color": (180, 160, 220)},
        ],
    },
    "hunter": {
        "name": "Охотник",
        "lines": [
            {"speaker": "Рейн",
             "role": "Охотник из Северных пределов",
             "text": "Тише. Видишь те следы? Теневой волк. Огромный. Прошёл здесь не больше часа назад. Они становятся всё смелее.",
             "portrait_color": (130, 115, 100)},
            {"speaker": "Герой",
             "role": "",
             "text": "Теневые волки? Насколько они опасны?",
             "portrait_color": (180, 200, 255)},
            {"speaker": "Рейн",
             "role": "Охотник из Северных пределов",
             "text": "Обычный волк отступит перед огнём. Теневой — нет. Он рождён из Тьмы, и Тьма не боится пламени. Ему нужен свет. Настоящий, божественный свет.",
             "portrait_color": (130, 115, 100)},
            {"speaker": "Рейн",
             "role": "Охотник из Северных пределов",
             "text": "Если собираешься в Туманный лес — загляни сначала в храм. Попроси благословение у жрицы. Без него ты не продержишься и ночи.",
             "portrait_color": (130, 115, 100)},
        ],
    },
}


def main():
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Тест диалогов (Genshin style)")

    clock = pygame.time.Clock()
    dialogue = DialogueBox(screen)

    font_title  = pygame.font.SysFont("georgia", 28, bold=True)
    font_sub    = pygame.font.SysFont("segoeui", 16)
    font_small  = pygame.font.SysFont("segoeui", 14)
    font_hint   = pygame.font.SysFont("segoeui", 12)

    dialogue_keys = list(DIALOGUES.keys())
    selected = 0
    mode = "select"  # select | dialogue | done

    # Фон — красивый пейзаж
    bg = pygame.Surface((1280, 720))
    # Небо
    for y in range(400):
        ratio = y / 400
        r = int(40 + ratio * 80)
        g = int(60 + ratio * 100)
        b = int(120 + ratio * 80)
        pygame.draw.line(bg, (r, g, b), (0, y), (1280, y))
    # Горы
    import math as m
    points = [(0, 720)]
    for x in range(0, 1281, 3):
        y = 350 + m.sin(x * 0.005) * 80 + m.sin(x * 0.01) * 40
        points.append((x, int(y)))
    points.append((1280, 720))
    pygame.draw.polygon(bg, (30, 45, 35), points)
    # Передний план
    points2 = [(0, 720)]
    for x in range(0, 1281, 3):
        y = 450 + m.sin(x * 0.008 + 2) * 60 + m.sin(x * 0.015) * 25
        points2.append((x, int(y)))
    points2.append((1280, 720))
    pygame.draw.polygon(bg, (20, 35, 25), points2)
    # Земля
    pygame.draw.rect(bg, (15, 25, 18), (0, 550, 1280, 170))

    def draw_selector():
        sw, sh = screen.get_size()
        panel_w = 400
        panel_h = len(DIALOGUES) * 65 + 100
        panel_x = sw // 2 - panel_w // 2
        panel_y = sh // 2 - panel_h // 2

        surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (10, 10, 18, 230),
                         surf.get_rect(), border_radius=14)
        pygame.draw.rect(surf, (100, 90, 120, 150),
                         surf.get_rect(), width=1, border_radius=14)
        screen.blit(surf, (panel_x, panel_y))

        title_s = font_title.render("Выбор диалога", True, (255, 255, 255))
        screen.blit(title_s,
                    (panel_x + panel_w // 2 - title_s.get_width() // 2,
                     panel_y + 18))

        for i, key in enumerate(dialogue_keys):
            data = DIALOGUES[key]
            is_sel = (i == selected)
            iy = panel_y + 70 + i * 65

            item = pygame.Surface((panel_w - 40, 55), pygame.SRCALPHA)
            if is_sel:
                pygame.draw.rect(item, (255, 255, 255, 20),
                                 item.get_rect(), border_radius=8)
                pygame.draw.rect(item, (255, 255, 255, 120),
                                 item.get_rect(), width=1, border_radius=8)
            else:
                pygame.draw.rect(item, (255, 255, 255, 8),
                                 item.get_rect(), border_radius=8)
            screen.blit(item, (panel_x + 20, iy))

            # Номер
            num_col = (255, 255, 255) if is_sel else (120, 120, 130)
            screen.blit(font_sub.render(f"[{i+1}]", True, num_col),
                        (panel_x + 30, iy + 8))

            # Имя
            name_col = (255, 255, 255) if is_sel else (180, 180, 190)
            screen.blit(font_small.render(data["name"], True, name_col),
                        (panel_x + 70, iy + 6))

            # Реплик
            count = f"{len(data['lines'])} реплик"
            screen.blit(font_hint.render(count, True, (120, 120, 130)),
                        (panel_x + 70, iy + 28))

            # Первая строка диалога
            first = data["lines"][0]["speaker"]
            screen.blit(font_hint.render(first, True, (100, 100, 110)),
                        (panel_x + 180, iy + 28))

        # Подсказка
        hint = "↑↓ / 1-5  выбор     ENTER  запуск     ESC  выход"
        screen.blit(font_hint.render(hint, True, (100, 100, 110)),
                    (panel_x + panel_w // 2 - font_hint.size(hint)[0] // 2,
                     panel_y + panel_h - 25))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if mode == "select":
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(dialogue_keys)
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(dialogue_keys)
                    for i in range(len(dialogue_keys)):
                        if event.key == getattr(pygame, f"K_{i+1}", None):
                            selected = i
                    if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                        key = dialogue_keys[selected]
                        dialogue.start_dialogue(DIALOGUES[key]["lines"])
                        mode = "dialogue"

                elif mode == "dialogue":
                    if event.key == pygame.K_ESCAPE:
                        dialogue.active = False
                        mode = "select"

                elif mode == "done":
                    if event.key == pygame.K_ESCAPE:
                        mode = "select"
                    if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                        key = dialogue_keys[selected]
                        dialogue.start_dialogue(DIALOGUES[key]["lines"])
                        mode = "dialogue"

            if mode == "dialogue":
                if dialogue.handle_event(event):
                    if not dialogue.active:
                        mode = "done"

        dialogue.update(dt)

        # Отрисовка
        screen.blit(bg, (0, 0))

        if mode == "select":
            draw_selector()
        elif mode == "dialogue":
            dialogue.draw()
        elif mode == "done":
            # Подсказка
            hint = "ENTER — повтор  |  ESC — к выбору"
            hs = font_hint.render(hint, True, (150, 150, 160))
            screen.blit(hs, (640 - hs.get_width() // 2, 680))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()