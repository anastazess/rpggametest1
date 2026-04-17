"""
Тестовый скрипт для проверки системы уведомлений.
Запуск: python test_notifications.py
"""

import pygame
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.ui.notifications import NotificationManager, Notification
from game.menu.icons import Icons


def main():
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Тест уведомлений - Echoes of the Fallen")

    clock = pygame.time.Clock()
    notification_manager = NotificationManager(screen)

    # Шрифты для UI
    font_title = pygame.font.SysFont("georgia", 36, bold=True)
    font_text = pygame.font.SysFont("segoeui", 18)
    font_hint = pygame.font.SysFont("segoeui", 14)

    # Кнопки для тестирования
    buttons = [
        {"key": pygame.K_1, "text": "[1] Информация",
         "action": lambda: notification_manager.show(
             "Это информационное сообщение",
             Notification.TYPE_INFO
         )},
        {"key": pygame.K_2, "text": "[2] Успех",
         "action": lambda: notification_manager.show_success(
             "Операция выполнена успешно!"
         )},
        {"key": pygame.K_3, "text": "[3] Предупреждение",
         "action": lambda: notification_manager.show_warning(
             "Внимание! Низкий уровень здоровья"
         )},
        {"key": pygame.K_4, "text": "[4] Ошибка",
         "action": lambda: notification_manager.show_error(
             "Не удалось сохранить игру"
         )},
        {"key": pygame.K_5, "text": "[5] Достижение",
         "action": lambda: notification_manager.show_achievement(
             "Первые шаги",
             "Начните своё приключение",
             Icons.draw_sword
         )},
        {"key": pygame.K_6, "text": "[6] Достижение 2",
         "action": lambda: notification_manager.show_achievement(
             "Истребитель монстров",
             "Победите 10 монстров",
             Icons.draw_trophy
         )},
        {"key": pygame.K_7, "text": "[7] Несколько сразу",
         "action": lambda: [
             notification_manager.show("Первое уведомление", Notification.TYPE_INFO),
             notification_manager.show("Второе уведомление", Notification.TYPE_SUCCESS),
             notification_manager.show("Третье уведомление", Notification.TYPE_WARNING),
         ]},
        {"key": pygame.K_8, "text": "[8] С иконкой",
         "action": lambda: notification_manager.show(
             "Настройки сохранены",
             Notification.TYPE_SUCCESS,
             title="Сохранение",
             icon_func=Icons.draw_save
         )},
        {"key": pygame.K_9, "text": "[9] Длинный текст",
         "action": lambda: notification_manager.show(
             "Это очень длинное уведомление для проверки переноса",
             Notification.TYPE_INFO,
             title="Тест длинного текста",
             duration=6.0
         )},
        {"key": pygame.K_0, "text": "[0] Очередь (5 штук)",
         "action": lambda: [
             notification_manager.show(f"Уведомление #{i + 1}", Notification.TYPE_INFO)
             for i in range(5)
         ]},
    ]

    # Генерация фона
    def generate_background():
        bg = pygame.Surface((1280, 720))
        for y in range(720):
            ratio = y / 720
            r = int(10 + ratio * 15)
            g = int(8 + ratio * 12)
            b = int(25 + ratio * 20)
            pygame.draw.line(bg, (r, g, b), (0, y), (1280, y))
        return bg

    background = generate_background()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Проверяем кнопки
                for btn in buttons:
                    if event.key == btn["key"]:
                        btn["action"]()

        # Обновление
        notification_manager.update(dt)

        # Отрисовка
        screen.blit(background, (0, 0))

        # Заголовок
        title_surf = font_title.render("Тест системы уведомлений", True, COLOR_PRIMARY_LIGHT)
        screen.blit(title_surf, (1280 // 2 - title_surf.get_width() // 2, 30))

        # Инструкции
        y = 100
        for btn in buttons:
            text_surf = font_text.render(btn["text"], True, COLOR_TEXT)
            screen.blit(text_surf, (100, y))
            y += 35

        # Подсказка
        hint_text = "ESC — выход  |  Нажимайте клавиши для тестирования уведомлений"
        hint_surf = font_hint.render(hint_text, True, COLOR_TEXT_DIM)
        screen.blit(hint_surf, (1280 // 2 - hint_surf.get_width() // 2, 680))

        # Уведомления поверх всего
        notification_manager.draw()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()