"""
Редактор локаций — Echoes of the Fallen
Создавайте и редактируйте карты, размещайте объекты, экспортируйте код.

Запуск: python world_editor.py

Управление:
  ЛКМ          — разместить / выбрать объект
  ПКМ          — удалить объект
  WASD         — двигать камеру
  Колёсико     — масштаб
  TAB          — переключить панель инструментов
  G            — показать/скрыть сетку
  CTRL+S       — сохранить в JSON
  CTRL+Z       — отменить последнее действие
  CTRL+E       — экспорт в Python-код
  DEL          — удалить выбранный объект
  ESC          — выход
"""

import pygame
import json
import math
import random
import os
import sys
import copy
import re
import ast

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *

# ══════════════════════════════════════════════════════════════════════
# Константы
# ══════════════════════════════════════════════════════════════════════

SCREEN_W, SCREEN_H = 1500, 850
GRID_SIZE = 40
TOOLBAR_W = 300

TOOL_CATEGORIES = {
    "Ландшафт": [
        {"id": "grass",    "name": "Трава",         "color": (55, 95, 45),   "size": (40, 40)},
        {"id": "dirt",     "name": "Земля",         "color": (100, 80, 60),  "size": (40, 40)},
        {"id": "stone",    "name": "Камень",        "color": (120, 115, 110),"size": (40, 40)},
        {"id": "water",    "name": "Вода",          "color": (60, 110, 180), "size": (40, 40)},
        {"id": "sand",     "name": "Песок",         "color": (200, 185, 140),"size": (40, 40)},
        {"id": "wheat",    "name": "Пшеница",       "color": (190, 170, 80), "size": (40, 40)},
    ],
    "Дороги": [
        {"id": "road_h",   "name": "Дорога (гориз)","color": (95, 80, 65),   "size": (120, 40)},
        {"id": "road_v",   "name": "Дорога (верт)", "color": (95, 80, 65),   "size": (40, 120)},
        {"id": "road_cross","name": "Перекрёсток",  "color": (95, 80, 65),   "size": (80, 80)},
        {"id": "path_h",   "name": "Тропа (гориз)", "color": (110, 95, 75),  "size": (80, 30)},
        {"id": "path_v",   "name": "Тропа (верт)",  "color": (110, 95, 75),  "size": (30, 80)},
        {"id": "plaza",    "name": "Площадь",       "color": (85, 75, 65),   "size": (160, 160)},
    ],
    "Природа": [
        {"id": "tree",      "name": "Дерево",       "color": (45, 85, 42),   "size": (50, 55), "solid": True},
        {"id": "tree_big",  "name": "Большое дерево","color": (40, 80, 38),  "size": (65, 70), "solid": True},
        {"id": "bush",      "name": "Куст",         "color": (55, 100, 50),  "size": (30, 25)},
        {"id": "rock",      "name": "Камень",       "color": (110, 105, 100),"size": (25, 18), "solid": True},
        {"id": "rock_big",  "name": "Большой камень","color": (100, 95, 90), "size": (45, 30), "solid": True},
        {"id": "flower_r",  "name": "Цветок красн", "color": (255, 100, 100),"size": (8, 8)},
        {"id": "flower_y",  "name": "Цветок жёлт",  "color": (255, 200, 80), "size": (8, 8)},
        {"id": "flower_p",  "name": "Цветок фиол",  "color": (200, 100, 255),"size": (8, 8)},
        {"id": "stump",     "name": "Пень",         "color": (90, 70, 50),   "size": (30, 25), "solid": True},
        {"id": "log",       "name": "Бревно",       "color": (100, 75, 50),  "size": (60, 20)},
        {"id": "mushroom",  "name": "Гриб",         "color": (180, 60, 50),  "size": (12, 15)},
    ],
    "Строения": [
        {"id": "house",     "name": "Дом",          "color": (120, 100, 80), "size": (100, 90), "solid": True},
        {"id": "house_big", "name": "Большой дом",  "color": (110, 90, 75),  "size": (130, 110), "solid": True},
        {"id": "barn",      "name": "Амбар",        "color": (130, 65, 55),  "size": (120, 100), "solid": True},
        {"id": "mill",      "name": "Мельница",     "color": (140, 120, 100),"size": (100, 130), "solid": True},
        {"id": "well",      "name": "Колодец",      "color": (110, 100, 95), "size": (40, 40),   "solid": True},
        {"id": "fountain",  "name": "Фонтан",       "color": (120, 115, 110),"size": (60, 60),   "solid": True},
        {"id": "fence_h",   "name": "Забор (гориз)", "color": (100, 80, 55), "size": (80, 6),    "solid": True},
        {"id": "fence_v",   "name": "Забор (верт)",  "color": (100, 80, 55), "size": (6, 80),    "solid": True},
        {"id": "bench",     "name": "Скамейка",     "color": (100, 75, 55),  "size": (50, 20)},
        {"id": "sign",      "name": "Указатель",    "color": (90, 70, 50),   "size": (20, 35),   "solid": True},
        {"id": "lamp",      "name": "Фонарь",       "color": (60, 55, 50),   "size": (15, 40),   "solid": True},
    ],
    "Зоны": [
        {"id": "spawn",      "name": "Точка спавна", "color": (100, 255, 100), "size": (32, 48)},
        {"id": "transition", "name": "Переход",      "color": (255, 200, 50),  "size": (40, 100)},
        {"id": "collider",   "name": "Коллайдер",    "color": (255, 60, 60),   "size": (40, 40), "solid": True},
        {"id": "trigger",    "name": "Триггер",      "color": (60, 200, 255),  "size": (60, 60)},
        {"id": "npc_spot",   "name": "Место NPC",    "color": (255, 150, 255), "size": (32, 48)},
    ],
}


# ══════════════════════════════════════════════════════════════════════
# Объект на карте
# ══════════════════════════════════════════════════════════════════════

class MapObject:
    _next_id = 1

    def __init__(self, obj_type, x, y, w, h, color, solid=False, props=None):
        self.uid = MapObject._next_id
        MapObject._next_id += 1
        self.obj_type = obj_type
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.solid = solid
        self.props = props or {}

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def to_dict(self):
        return {
            "type": self.obj_type, "x": self.x, "y": self.y,
            "w": self.w, "h": self.h,
            "color": list(self.color), "solid": self.solid,
            "props": self.props,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["type"], d["x"], d["y"], d["w"], d["h"],
                   tuple(d["color"]), d.get("solid", False), d.get("props", {}))


# ══════════════════════════════════════════════════════════════════════
# Данные карты
# ══════════════════════════════════════════════════════════════════════

class MapData:
    def __init__(self, name="Новая локация", width=1200, height=900):
        self.name = name
        self.width = width
        self.height = height
        self.bg_color = (50, 85, 40)
        self.objects: list[MapObject] = []

    def add(self, obj: MapObject):
        self.objects.append(obj)

    def remove(self, obj: MapObject):
        self.objects = [o for o in self.objects if o.uid != obj.uid]

    def get_at(self, x, y):
        for obj in reversed(self.objects):
            if obj.rect.collidepoint(x, y):
                return obj
        return None

    def to_dict(self):
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "bg_color": list(self.bg_color),
            "objects": [o.to_dict() for o in self.objects],
        }

    @classmethod
    def from_dict(cls, d):
        m = cls(d["name"], d["width"], d["height"])
        m.bg_color = tuple(d.get("bg_color", (50, 85, 40)))
        for od in d.get("objects", []):
            m.objects.append(MapObject.from_dict(od))
        return m

    def save_json(self, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_json(cls, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_dict(json.load(f))

    def export_python(self):
        lines = []
        safe = self.name.lower().replace(" ", "_").replace("-", "_")
        lines.append(f'"""Локация: {self.name} — сгенерировано редактором."""')
        lines.append(f"import pygame\n")
        lines.append(f"MAP_NAME   = \"{self.name}\"")
        lines.append(f"MAP_WIDTH  = {self.width}")
        lines.append(f"MAP_HEIGHT = {self.height}")
        lines.append(f"MAP_BG     = {self.bg_color}\n")

        roads      = [o for o in self.objects if o.obj_type.startswith("road") or
                       o.obj_type.startswith("path") or o.obj_type == "plaza"]
        terrain    = [o for o in self.objects if o.obj_type in
                      ("grass","dirt","stone","water","sand","wheat")]
        trees      = [o for o in self.objects if o.obj_type.startswith("tree")]
        rocks      = [o for o in self.objects if o.obj_type.startswith("rock")]
        flowers    = [o for o in self.objects if o.obj_type.startswith("flower")]
        buildings  = [o for o in self.objects if o.obj_type in
                      ("house","house_big","barn","mill")]
        furniture  = [o for o in self.objects if o.obj_type in
                      ("well","fountain","bench","sign","lamp","fence_h","fence_v",
                       "stump","log","mushroom","bush")]
        zones      = [o for o in self.objects if o.obj_type in
                      ("spawn","transition","collider","trigger","npc_spot")]

        def emit_list(name, objs):
            lines.append(f"\n{name} = [")
            for o in objs:
                lines.append(f"    {{\"type\": \"{o.obj_type}\", "
                             f"\"x\": {o.x}, \"y\": {o.y}, "
                             f"\"w\": {o.w}, \"h\": {o.h}, "
                             f"\"color\": {o.color}, "
                             f"\"solid\": {o.solid}"
                             + (f", \"props\": {o.props}" if o.props else "")
                             + "},")
            lines.append("]")

        if roads:    emit_list("ROADS",     roads)
        if terrain:  emit_list("TERRAIN",   terrain)
        if trees:    emit_list("TREES",     trees)
        if rocks:    emit_list("ROCKS",     rocks)
        if flowers:  emit_list("FLOWERS",   flowers)
        if buildings:emit_list("BUILDINGS", buildings)
        if furniture:emit_list("FURNITURE", furniture)
        if zones:    emit_list("ZONES",     zones)

        colliders = [o for o in self.objects if o.solid]
        lines.append(f"\n\nCOLLIDERS = [")
        for o in colliders:
            lines.append(f"    pygame.Rect({o.x}, {o.y}, {o.w}, {o.h}),")
        lines.append("]")

        spawns = [o for o in self.objects if o.obj_type == "spawn"]
        if spawns:
            s = spawns[0]
            lines.append(f"\nSPAWN_X = {s.x}")
            lines.append(f"SPAWN_Y = {s.y}")

        trans = [o for o in self.objects if o.obj_type == "transition"]
        if trans:
            lines.append(f"\nTRANSITIONS = [")
            for t in trans:
                label = t.props.get("label", "Переход")
                target = t.props.get("target", "unknown")
                lines.append(f"    {{\"rect\": pygame.Rect({t.x}, {t.y}, {t.w}, {t.h}), "
                             f"\"target\": \"{target}\", \"label\": \"{label}\"}},")
            lines.append("]")

        lines.append(f"\n\n# Всего объектов: {len(self.objects)}")
        lines.append(f"# Коллайдеров: {len(colliders)}")
        return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════
# Парсер Python-файлов локаций
# ══════════════════════════════════════════════════════════════════════

class PythonMapParser:
    """Парсит Python-файл локации и превращает в MapData."""

    @staticmethod
    def parse_file(filepath: str) -> MapData:
        """Загружает Python-файл и извлекает данные карты."""
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        m = MapData()
        m.name = PythonMapParser._extract_string(source, "MAP_NAME", "Загруженная карта")
        m.width = PythonMapParser._extract_int(source, "MAP_WIDTH", 1200)
        m.height = PythonMapParser._extract_int(source, "MAP_HEIGHT", 900)
        m.bg_color = PythonMapParser._extract_tuple(source, "MAP_BG", (50, 85, 40))

        # Списки объектов
        list_names = [
            "ROADS", "TERRAIN", "TREES", "ROCKS", "FLOWERS",
            "BUILDINGS", "FURNITURE", "ZONES", "TRANSITIONS",
        ]
        for list_name in list_names:
            items = PythonMapParser._extract_list(source, list_name)
            for item in items:
                obj = MapObject(
                    item.get("type", "unknown"),
                    item.get("x", 0),
                    item.get("y", 0),
                    item.get("w", 40),
                    item.get("h", 40),
                    tuple(item.get("color", (100, 100, 100))),
                    item.get("solid", False),
                    item.get("props", {}),
                )
                m.objects.append(obj)

        # Точка спавна
        spawn_x = PythonMapParser._extract_int(source, "SPAWN_X", -1)
        spawn_y = PythonMapParser._extract_int(source, "SPAWN_Y", -1)
        if spawn_x >= 0 and spawn_y >= 0:
            # Проверяем что спавн ещё не добавлен
            has_spawn = any(o.obj_type == "spawn" for o in m.objects)
            if not has_spawn:
                m.objects.append(MapObject(
                    "spawn", spawn_x, spawn_y, 32, 48, (100, 255, 100)
                ))

        return m

    @staticmethod
    def _extract_string(source, var_name, default=""):
        pattern = rf'{var_name}\s*=\s*["\'](.+?)["\']'
        match = re.search(pattern, source)
        return match.group(1) if match else default

    @staticmethod
    def _extract_int(source, var_name, default=0):
        pattern = rf'{var_name}\s*=\s*(\d+)'
        match = re.search(pattern, source)
        return int(match.group(1)) if match else default

    @staticmethod
    def _extract_tuple(source, var_name, default=(0, 0, 0)):
        pattern = rf'{var_name}\s*=\s*\((.+?)\)'
        match = re.search(pattern, source)
        if match:
            try:
                vals = [int(v.strip()) for v in match.group(1).split(",")]
                return tuple(vals[:3])
            except (ValueError, IndexError):
                pass
        return default

    @staticmethod
    def _extract_list(source, var_name):
        """Извлекает список словарей из Python-кода."""
        # Ищем блок VARNAME = [ ... ]
        pattern = rf'{var_name}\s*=\s*\[(.*?)\]'
        match = re.search(pattern, source, re.DOTALL)
        if not match:
            return []

        block = match.group(1)
        items = []

        # Ищем каждый { ... } словарь
        dict_pattern = r'\{(.+?)\}'
        for dict_match in re.finditer(dict_pattern, block, re.DOTALL):
            raw = dict_match.group(1)
            item = PythonMapParser._parse_dict_content(raw)
            if item:
                items.append(item)

        return items

    @staticmethod
    def _parse_dict_content(raw: str) -> dict:
        """Парсит содержимое одного словаря."""
        result = {}

        # type
        m = re.search(r'"type"\s*:\s*"(.+?)"', raw)
        if m:
            result["type"] = m.group(1)

        # Числовые поля
        for field in ["x", "y", "w", "h"]:
            m = re.search(rf'"{field}"\s*:\s*(-?\d+)', raw)
            if m:
                result[field] = int(m.group(1))

        # color как кортеж
        m = re.search(r'"color"\s*:\s*\((.+?)\)', raw)
        if m:
            try:
                result["color"] = [int(v.strip()) for v in m.group(1).split(",")]
            except ValueError:
                result["color"] = [100, 100, 100]

        # solid
        m = re.search(r'"solid"\s*:\s*(True|False)', raw)
        if m:
            result["solid"] = m.group(1) == "True"

        # props
        m = re.search(r'"props"\s*:\s*\{(.+?)\}', raw)
        if m:
            props = {}
            for pm in re.finditer(r'"(\w+)"\s*:\s*"(.+?)"', m.group(1)):
                props[pm.group(1)] = pm.group(2)
            result["props"] = props

        # Для transition-ов из TRANSITIONS списка
        m = re.search(r'"target"\s*:\s*"(.+?)"', raw)
        if m and "type" not in result:
            result["type"] = "transition"
            result["props"] = result.get("props", {})
            result["props"]["target"] = m.group(1)

        m2 = re.search(r'"label"\s*:\s*"(.+?)"', raw)
        if m2:
            result["props"] = result.get("props", {})
            result["props"]["label"] = m2.group(1)

        # rect из TRANSITIONS: pygame.Rect(x, y, w, h)
        m = re.search(r'pygame\.Rect\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', raw)
        if m and "x" not in result:
            result["x"] = int(m.group(1))
            result["y"] = int(m.group(2))
            result["w"] = int(m.group(3))
            result["h"] = int(m.group(4))
            result["color"] = result.get("color", [255, 200, 50])
            result["solid"] = False

        return result if "type" in result or "x" in result else None


class PythonMapMerger:
    """Мержит изменения обратно в исходный Python-файл."""

    @staticmethod
    def merge(original_filepath: str, map_data: MapData) -> str:
        """
        Берёт оригинальный файл и заменяет/добавляет данные из редактора.
        Сохраняет комментарии и пользовательский код.
        """
        try:
            with open(original_filepath, 'r', encoding='utf-8') as f:
                original = f.read()
        except FileNotFoundError:
            original = ""

        # Генерируем новый код из MapData
        new_code = map_data.export_python()

        if not original.strip():
            return new_code

        # Стратегия: берём оригинал, заменяем блоки данных
        result_lines = []
        original_lines = original.split("\n")

        # Собираем какие блоки есть в новом коде
        new_blocks = {}
        new_lines = new_code.split("\n")
        current_block = None
        current_block_lines = []

        for line in new_lines:
            stripped = line.strip()

            # Определяем начало блока
            block_match = re.match(r'^(\w+)\s*=', stripped)
            if block_match:
                if current_block:
                    new_blocks[current_block] = "\n".join(current_block_lines)
                current_block = block_match.group(1)
                current_block_lines = [line]
            elif current_block:
                current_block_lines.append(line)
                # Конец блока — закрывающая ]
                if stripped == "]" or (not stripped.startswith(" ") and
                                        not stripped.startswith("#") and
                                        stripped and current_block_lines):
                    if stripped == "]":
                        new_blocks[current_block] = "\n".join(current_block_lines)
                        current_block = None
                        current_block_lines = []

        if current_block:
            new_blocks[current_block] = "\n".join(current_block_lines)

        # Теперь проходим по оригиналу и заменяем блоки
        replaced_blocks = set()
        skip_until_bracket = False
        i = 0

        while i < len(original_lines):
            line = original_lines[i]
            stripped = line.strip()

            # Проверяем начало блока для замены
            block_match = re.match(r'^(\w+)\s*=', stripped)
            if block_match:
                block_name = block_match.group(1)
                if block_name in new_blocks:
                    # Заменяем этот блок
                    result_lines.append(new_blocks[block_name])
                    replaced_blocks.add(block_name)

                    # Пропускаем старый блок
                    if "[" in stripped:
                        bracket_count = stripped.count("[") - stripped.count("]")
                        i += 1
                        while i < len(original_lines) and bracket_count > 0:
                            bracket_count += original_lines[i].count("[")
                            bracket_count -= original_lines[i].count("]")
                            i += 1
                        continue
                    else:
                        i += 1
                        continue

            result_lines.append(line)
            i += 1

        # Добавляем блоки которых не было в оригинале
        additions = []
        for block_name, block_code in new_blocks.items():
            if block_name not in replaced_blocks:
                additions.append("")
                additions.append(f"# === Добавлено редактором ===")
                additions.append(block_code)

        if additions:
            result_lines.extend(additions)

        # Обновляем метаданные
        final = "\n".join(result_lines)

        # Заменяем/добавляем MAP_NAME, MAP_WIDTH, MAP_HEIGHT, MAP_BG
        for var, val in [
            ("MAP_NAME", f'"{map_data.name}"'),
            ("MAP_WIDTH", str(map_data.width)),
            ("MAP_HEIGHT", str(map_data.height)),
            ("MAP_BG", str(map_data.bg_color)),
        ]:
            pattern = rf'^{var}\s*=\s*.+$'
            replacement = f'{var} = {val}'
            if re.search(pattern, final, re.MULTILINE):
                final = re.sub(pattern, replacement, final, flags=re.MULTILINE)
            else:
                final = f'{replacement}\n{final}'

        # Добавляем комментарий с датой
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        if "# Последнее изменение:" in final:
            final = re.sub(r'# Последнее изменение:.*',
                           f'# Последнее изменение: {timestamp}', final)
        else:
            final += f'\n\n# Последнее изменение: {timestamp}'
            final += f'\n# Изменено через редактор локаций'

        return final

# ══════════════════════════════════════════════════════════════════════
# Загрузка существующих локаций
# ══════════════════════════════════════════════════════════════════════

def load_city_map():
    """Импортирует город как MapData."""
    m = MapData("Валенхольм (город)", 1800, 1400)
    m.bg_color = (50, 85, 40)

    roads = [
        (0, 500, 1800, 100), (400, 0, 100, 1400),
        (1000, 200, 80, 900), (400, 900, 700, 80), (350, 450, 200, 200),
    ]
    for rx, ry, rw, rh in roads:
        m.add(MapObject("road_h" if rw > rh else "road_v",
                         rx, ry, rw, rh, (95, 80, 65)))

    buildings = [
        ("house_big", 200, 180, 120, 100), ("house", 550, 220, 100, 90),
        ("house_big", 750, 250, 130, 95), ("house", 200, 700, 110, 95),
        ("house", 550, 700, 100, 90), ("house", 700, 720, 90, 85),
        ("house", 1150, 300, 110, 95), ("house", 1150, 500, 100, 90),
        ("house_big", 1150, 750, 120, 100),
        ("house_big", 550, 1050, 130, 100), ("house", 150, 1050, 100, 90),
        ("house_big", 900, 700, 200, 160),
    ]
    for bt, bx, by, bw, bh in buildings:
        m.add(MapObject(bt, bx, by, bw, bh, (120, 100, 80), solid=True))

    m.add(MapObject("fountain", 420, 510, 60, 60, (120, 115, 110), solid=True))

    for wx, wy in [(750, 850), (1100, 450)]:
        m.add(MapObject("well", wx, wy, 40, 40, (110, 100, 95), solid=True))

    m.add(MapObject("spawn", 450, 680, 32, 48, (100, 255, 100)))

    return m


def load_fields_map():
    """Импортирует поля как MapData."""
    m = MapData("Поля Валенхольма", 2000, 1600)
    m.bg_color = (65, 110, 50)

    roads = [
        (0, 700, 500, 80), (500, 740, 800, 40),
        (800, 780, 40, 400), (1300, 400, 40, 380), (1340, 400, 660, 40),
    ]
    for rx, ry, rw, rh in roads:
        m.add(MapObject("path_h" if rw > rh else "path_v",
                         rx, ry, rw, rh, (120, 100, 75)))

    for fx, fy, fw, fh in [(100,100,250,250),(900,100,300,250),
                            (100,900,300,300),(1400,600,350,300),(1400,1000,400,350)]:
        m.add(MapObject("wheat", fx, fy, fw, fh, (190, 170, 80)))

    m.add(MapObject("house", 400, 400, 110, 90, (120, 100, 80), solid=True))
    m.add(MapObject("barn", 600, 350, 120, 100, (130, 65, 55), solid=True))
    m.add(MapObject("mill", 1250, 200, 100, 130, (140, 120, 100), solid=True))
    m.add(MapObject("well", 520, 580, 40, 40, (110, 100, 95), solid=True))

    for fx, fy, fw, fh in [(350,350,5,300),(350,350,400,5),
                            (750,350,5,300),(350,650,400,5)]:
        m.add(MapObject("fence_h" if fw > fh else "fence_v",
                         fx, fy, fw, fh, (100, 80, 55), solid=True))

    m.add(MapObject("spawn", 300, 730, 32, 48, (100, 255, 100)))
    m.add(MapObject("transition", 0, 690, 40, 100, (255, 200, 50),
                     props={"target": "city", "label": "В Валенхольм"}))

    return m


PRESETS = {
    "city": ("Валенхольм (город)", load_city_map),
    "fields": ("Поля Валенхольма", load_fields_map),
}


# ══════════════════════════════════════════════════════════════════════
# Отрисовка объектов
# ══════════════════════════════════════════════════════════════════════

def draw_map_object(surface, obj, cam_x, cam_y, selected=False):
    sx = int(obj.x - cam_x)
    sy = int(obj.y - cam_y)
    w, h = obj.w, obj.h
    t = obj.obj_type

    if t in ("grass", "dirt", "stone", "sand", "wheat", "water"):
        pygame.draw.rect(surface, obj.color, (sx, sy, w, h))
        if t == "water":
            for i in range(0, w, 15):
                pygame.draw.arc(surface, (100, 150, 220),
                                (sx + i, sy + h // 2 - 5, 12, 10), 0, math.pi, 2)
        elif t == "wheat":
            for i in range(sx, sx + w, 8):
                lh = random.randint(5, 12)
                pygame.draw.line(surface, (170, 150, 60), (i, sy + h), (i, sy + h - lh), 1)

    elif t.startswith("road") or t.startswith("path") or t == "plaza":
        pygame.draw.rect(surface, obj.color, (sx, sy, w, h))

    elif t in ("tree", "tree_big"):
        s = max(w, h)
        trunk_w = s // 5
        pygame.draw.rect(surface, (80, 55, 35),
                         (sx + w // 2 - trunk_w // 2, sy + h // 2, trunk_w, h // 2))
        pygame.draw.circle(surface, obj.color, (sx + w // 2, sy + h // 3), w // 2)
        lighter = tuple(min(255, c + 20) for c in obj.color)
        pygame.draw.circle(surface, lighter, (sx + w // 3, sy + h // 3), w // 3)

    elif t == "bush":
        pygame.draw.ellipse(surface, obj.color, (sx, sy, w, h))

    elif t.startswith("rock"):
        pygame.draw.ellipse(surface, obj.color, (sx, sy, w, h))
        pygame.draw.ellipse(surface, tuple(max(0, c - 20) for c in obj.color),
                            (sx, sy, w, h), width=1)

    elif t.startswith("flower"):
        pygame.draw.line(surface, (50, 100, 40), (sx + 4, sy + h), (sx + 4, sy + 4), 2)
        pygame.draw.circle(surface, obj.color, (sx + 4, sy + 4), 4)

    elif t in ("house", "house_big"):
        pygame.draw.rect(surface, obj.color, (sx, sy + 30, w, h - 30))
        pygame.draw.polygon(surface, tuple(max(0, c - 20) for c in obj.color),
                            [(sx - 8, sy + 35), (sx + w // 2, sy), (sx + w + 8, sy + 35)])
        pygame.draw.rect(surface, (65, 45, 30), (sx + w // 2 - 12, sy + h - 40, 24, 40))

    elif t == "barn":
        pygame.draw.rect(surface, obj.color, (sx, sy + 35, w, h - 35))
        pygame.draw.polygon(surface, tuple(max(0, c - 15) for c in obj.color),
                            [(sx - 8, sy + 40), (sx + w // 2, sy), (sx + w + 8, sy + 40)])

    elif t == "mill":
        pygame.draw.rect(surface, obj.color, (sx + 20, sy + 50, 60, 80))
        pygame.draw.polygon(surface, tuple(max(0, c - 15) for c in obj.color),
                            [(sx + 10, sy + 55), (sx + 50, sy + 20), (sx + 90, sy + 55)])
        lcx, lcy = sx + 50, sy + 45
        angle = pygame.time.get_ticks() / 1500
        for i in range(4):
            a = angle + i * math.pi / 2
            ex = lcx + int(35 * math.cos(a))
            ey = lcy + int(35 * math.sin(a))
            pygame.draw.line(surface, (130, 115, 95), (lcx, lcy), (ex, ey), 3)

    elif t == "well":
        pygame.draw.ellipse(surface, obj.color, (sx, sy + 15, w, h // 2))
        pygame.draw.rect(surface, (90, 80, 75), (sx + 5, sy, w - 10, h // 2))
        pygame.draw.rect(surface, (80, 65, 50), (sx + 2, sy - 12, w - 4, 8))

    elif t == "fountain":
        pygame.draw.ellipse(surface, obj.color, (sx, sy + h // 2, w, h // 2))
        pygame.draw.ellipse(surface, (80, 130, 180), (sx + 8, sy + h // 2 + 5, w - 16, h // 3))
        pygame.draw.rect(surface, (140, 130, 125), (sx + w // 2 - 4, sy + 10, 8, h // 2))

    elif t == "fence_h":
        for px in range(sx, sx + w, 20):
            pygame.draw.rect(surface, (90, 70, 50), (px, sy - 12, 4, 16))
        pygame.draw.line(surface, obj.color, (sx, sy - 8), (sx + w, sy - 8), 3)
        pygame.draw.line(surface, obj.color, (sx, sy - 2), (sx + w, sy - 2), 3)

    elif t == "fence_v":
        for py in range(sy, sy + h, 20):
            pygame.draw.rect(surface, (90, 70, 50), (sx - 2, py, 8, 4))
        pygame.draw.line(surface, obj.color, (sx, sy), (sx, sy + h), 3)
        pygame.draw.line(surface, obj.color, (sx + 4, sy), (sx + 4, sy + h), 3)

    elif t == "bench":
        pygame.draw.rect(surface, obj.color, (sx, sy, w, h // 2), border_radius=3)
        pygame.draw.rect(surface, (80, 60, 45), (sx + 5, sy + h // 2, 6, h // 2))
        pygame.draw.rect(surface, (80, 60, 45), (sx + w - 11, sy + h // 2, 6, h // 2))

    elif t == "sign":
        pygame.draw.rect(surface, obj.color, (sx + w // 2 - 3, sy + h // 2, 6, h // 2))
        pygame.draw.rect(surface, (110, 90, 65), (sx, sy, w, h // 2), border_radius=3)

    elif t == "lamp":
        pygame.draw.rect(surface, obj.color, (sx + w // 2 - 3, sy + 12, 6, h - 12))
        pygame.draw.circle(surface, (255, 220, 100), (sx + w // 2, sy + 8), 8)

    elif t in ("stump", "log", "mushroom"):
        pygame.draw.ellipse(surface, obj.color, (sx, sy, w, h))

    elif t == "spawn":
        pygame.draw.rect(surface, (*obj.color, 120), (sx, sy, w, h), border_radius=6)
        pygame.draw.rect(surface, obj.color, (sx, sy, w, h), width=2, border_radius=6)
        font = pygame.font.SysFont("segoeui", 10)
        surface.blit(font.render("SPAWN", True, obj.color), (sx + 1, sy + h // 2 - 5))

    elif t == "transition":
        a = int(120 + 60 * math.sin(pygame.time.get_ticks() / 400))
        ts = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(ts, (*obj.color, a), (0, 0, w, h), border_radius=6)
        pygame.draw.rect(ts, (*obj.color, 220), (0, 0, w, h), width=2, border_radius=6)
        surface.blit(ts, (sx, sy))
        font = pygame.font.SysFont("segoeui", 9)
        lbl = obj.props.get("label", "Переход")
        surface.blit(font.render(lbl, True, (255, 220, 80)), (sx + 3, sy + h // 2 - 5))

    elif t == "collider":
        cs = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(cs, (255, 60, 60, 60), (0, 0, w, h))
        pygame.draw.rect(cs, (255, 60, 60, 180), (0, 0, w, h), width=2)
        surface.blit(cs, (sx, sy))

    elif t == "trigger":
        cs = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(cs, (60, 200, 255, 50), (0, 0, w, h), border_radius=4)
        pygame.draw.rect(cs, (60, 200, 255, 160), (0, 0, w, h), width=2, border_radius=4)
        surface.blit(cs, (sx, sy))

    elif t == "npc_spot":
        pygame.draw.rect(surface, (*obj.color, 100), (sx, sy, w, h), border_radius=6)
        pygame.draw.rect(surface, obj.color, (sx, sy, w, h), width=2, border_radius=6)
        font = pygame.font.SysFont("segoeui", 9)
        surface.blit(font.render("NPC", True, obj.color), (sx + 5, sy + h // 2 - 5))

    else:
        pygame.draw.rect(surface, obj.color, (sx, sy, w, h))

    if selected:
        pygame.draw.rect(surface, COLOR_ACCENT, (sx - 2, sy - 2, w + 4, h + 4), width=3)


# ══════════════════════════════════════════════════════════════════════
# Главное окно
# ══════════════════════════════════════════════════════════════════════

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Редактор локаций — Echoes of the Fallen")
    clock = pygame.time.Clock()

    font_title   = pygame.font.SysFont("georgia", 20, bold=True)
    font_heading = pygame.font.SysFont("segoeui", 14, bold=True)
    font_normal  = pygame.font.SysFont("segoeui", 13)
    font_small   = pygame.font.SysFont("segoeui", 11)
    font_code    = pygame.font.SysFont("consolas", 11)
    font_btn     = pygame.font.SysFont("segoeui", 13, bold=True)

    # Состояние
    map_data = MapData()
    cam_x, cam_y = 0.0, 0.0
    zoom = 1.0

    selected_tool = None       # dict из TOOL_CATEGORIES
    selected_obj  = None       # MapObject
    selected_cat  = list(TOOL_CATEGORIES.keys())[0]

    show_grid = True
    show_toolbar = True
    undo_stack = []
    mode = "editor"            # editor | code_view | load_menu | props | resize

    code_text = ""
    code_scroll = 0

    # Свойства для resize
    resize_w = str(map_data.width)
    resize_h = str(map_data.height)
    resize_name = map_data.name
    resize_active = ""         # "w" | "h" | "name"
    resize_bg_r = str(map_data.bg_color[0])
    resize_bg_g = str(map_data.bg_color[1])
    resize_bg_b = str(map_data.bg_color[2])

    # Свойства для props
    props_target = ""
    props_label = ""
    props_active = ""

    notification = ""
    notif_timer = 0.0
    loaded_from_file = None  # Путь к загруженному .py файлу
    available_py_files = []
    available_json_files = []

    def show_notif(text):
        nonlocal notification, notif_timer
        notification = text
        notif_timer = 3.0

    def push_undo():
        undo_stack.append(copy.deepcopy(map_data.to_dict()))
        if len(undo_stack) > 50:
            undo_stack.pop(0)

    def do_undo():
        nonlocal map_data, selected_obj
        if undo_stack:
            d = undo_stack.pop()
            map_data = MapData.from_dict(d)
            selected_obj = None
            show_notif("Отменено")

    # ── Фон ──────────────────────────────────────────────────────────

    bg = pygame.Surface((SCREEN_W, SCREEN_H))
    for y in range(SCREEN_H):
        ratio = y / SCREEN_H
        bg.set_at((0, y), (0, 0, 0))
        pygame.draw.line(bg, (int(18 + ratio * 5), int(15 + ratio * 4), int(28 + ratio * 8)),
                         (0, y), (SCREEN_W, y))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if notif_timer > 0:
            notif_timer -= dt
        mouse = pygame.mouse.get_pos()

        # Мир-координаты мыши
        canvas_x = TOOLBAR_W if show_toolbar else 0
        world_mx = int((mouse[0] - canvas_x) / zoom + cam_x)
        world_my = int(mouse[1] / zoom + cam_y)

        # Привязка к сетке
        if show_grid:
            snap_x = (world_mx // GRID_SIZE) * GRID_SIZE
            snap_y = (world_my // GRID_SIZE) * GRID_SIZE
        else:
            snap_x = world_mx
            snap_y = world_my

        # ── События ──────────────────────────────────────────────────

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if mode == "code_view":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    mode = "editor"
                if event.type == pygame.MOUSEWHEEL:
                    code_scroll = max(0, code_scroll - event.y * 3)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    save_btn_r = pygame.Rect(SCREEN_W // 2 - 200, SCREEN_H - 55, 180, 38)
                    close_btn_r = pygame.Rect(SCREEN_W // 2 + 20, SCREEN_H - 55, 180, 38)

                    if save_btn_r.collidepoint(event.pos):
                        if loaded_from_file:
                            # Бэкап
                            backup = loaded_from_file + ".backup"
                            if os.path.exists(loaded_from_file):
                                import shutil
                                shutil.copy2(loaded_from_file, backup)
                            with open(loaded_from_file, 'w', encoding='utf-8') as f:
                                f.write(code_text)
                            show_notif(f"Сохранено: {loaded_from_file}")
                        else:
                            fname = map_data.name.lower().replace(" ", "_") + "_map.py"
                            with open(fname, 'w', encoding='utf-8') as f:
                                f.write(code_text)
                            loaded_from_file = fname
                            show_notif(f"Создан: {fname}")
                        mode = "editor"

                    if close_btn_r.collidepoint(event.pos):
                        mode = "editor"
                continue

            if mode == "load_menu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    mode = "editor"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    menu_x = SCREEN_W // 2 - 220
                    menu_y = 120

                    # Новая карта
                    if pygame.Rect(menu_x + 10, menu_y + 55, 420, 38).collidepoint(event.pos):
                        map_data = MapData()
                        selected_obj = None
                        undo_stack.clear()
                        loaded_from_file = None
                        mode = "editor"
                        show_notif("Новая карта создана")

                    # Пресеты
                    for i, (key, (pname, pfunc)) in enumerate(PRESETS.items()):
                        r = pygame.Rect(menu_x + 10, menu_y + 110 + i * 48, 420, 38)
                        if r.collidepoint(event.pos):
                            map_data = pfunc()
                            selected_obj = None
                            undo_stack.clear()
                            loaded_from_file = None
                            mode = "editor"
                            show_notif(f"Загружено: {pname}")

                    # Python файлы
                    py_start_y = menu_y + 110 + len(PRESETS) * 48 + 30
                    for fi, py_file in enumerate(available_py_files):
                        r = pygame.Rect(menu_x + 10, py_start_y + fi * 40, 420, 34)
                        if r.collidepoint(event.pos):
                            try:
                                map_data = PythonMapParser.parse_file(py_file)
                                selected_obj = None
                                undo_stack.clear()
                                loaded_from_file = py_file
                                mode = "editor"
                                show_notif(f"Python загружен: {py_file} ({len(map_data.objects)} объектов)")
                            except Exception as e:
                                show_notif(f"Ошибка: {e}")

                    # JSON файлы
                    json_start_y = py_start_y + len(available_py_files) * 40 + 30
                    for fi, json_file in enumerate(available_json_files):
                        r = pygame.Rect(menu_x + 10, json_start_y + fi * 40, 420, 34)
                        if r.collidepoint(event.pos):
                            try:
                                map_data = MapData.load_json(json_file)
                                selected_obj = None
                                undo_stack.clear()
                                loaded_from_file = None
                                mode = "editor"
                                show_notif(f"JSON загружен: {json_file}")
                            except Exception as e:
                                show_notif(f"Ошибка: {e}")
                continue

            if mode == "resize":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mode = "editor"
                    elif event.key == pygame.K_RETURN:
                        try:
                            nw = max(400, int(resize_w))
                            nh = max(400, int(resize_h))
                            push_undo()
                            map_data.width = nw
                            map_data.height = nh
                            map_data.name = resize_name
                            map_data.bg_color = (
                                max(0, min(255, int(resize_bg_r))),
                                max(0, min(255, int(resize_bg_g))),
                                max(0, min(255, int(resize_bg_b))),
                            )
                            mode = "editor"
                            show_notif(f"Карта: {nw}x{nh}")
                        except ValueError:
                            show_notif("Ошибка значений")
                    elif event.key == pygame.K_BACKSPACE:
                        if resize_active == "w": resize_w = resize_w[:-1]
                        elif resize_active == "h": resize_h = resize_h[:-1]
                        elif resize_active == "name": resize_name = resize_name[:-1]
                        elif resize_active == "r": resize_bg_r = resize_bg_r[:-1]
                        elif resize_active == "g": resize_bg_g = resize_bg_g[:-1]
                        elif resize_active == "b": resize_bg_b = resize_bg_b[:-1]
                    elif event.unicode:
                        if resize_active == "w": resize_w += event.unicode
                        elif resize_active == "h": resize_h += event.unicode
                        elif resize_active == "name": resize_name += event.unicode
                        elif resize_active == "r": resize_bg_r += event.unicode
                        elif resize_active == "g": resize_bg_g += event.unicode
                        elif resize_active == "b": resize_bg_b += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    dx = SCREEN_W // 2 - 150
                    dy = 200
                    fields = [("name", dy+30), ("w", dy+85), ("h", dy+140),
                              ("r", dy+210), ("g", dy+250), ("b", dy+290)]
                    resize_active = ""
                    for fname, fy in fields:
                        if pygame.Rect(dx+80, fy, 200, 26).collidepoint(event.pos):
                            resize_active = fname
                continue

            if mode == "props":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        if selected_obj:
                            selected_obj.props["target"] = props_target
                            selected_obj.props["label"] = props_label
                        mode = "editor"
                    elif event.key == pygame.K_BACKSPACE:
                        if props_active == "target": props_target = props_target[:-1]
                        elif props_active == "label": props_label = props_label[:-1]
                    elif event.unicode:
                        if props_active == "target": props_target += event.unicode
                        elif props_active == "label": props_label += event.unicode
                    elif event.key == pygame.K_TAB:
                        props_active = "label" if props_active == "target" else "target"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    dx = SCREEN_W // 2 - 150
                    if pygame.Rect(dx+80, 260, 200, 26).collidepoint(event.pos):
                        props_active = "target"
                    elif pygame.Rect(dx+80, 310, 200, 26).collidepoint(event.pos):
                        props_active = "label"
                continue

            # ── Режим редактора ───────────────────────────────────────

            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                if event.key == pygame.K_ESCAPE:
                    if selected_tool:
                        selected_tool = None
                    elif selected_obj:
                        selected_obj = None
                    else:
                        running = False

                if event.key == pygame.K_TAB:
                    show_toolbar = not show_toolbar
                if event.key == pygame.K_g:
                    show_grid = not show_grid

                if event.key == pygame.K_DELETE and selected_obj:
                    push_undo()
                    map_data.remove(selected_obj)
                    selected_obj = None
                    show_notif("Объект удалён")

                if event.key == pygame.K_z and mods & pygame.KMOD_CTRL:
                    do_undo()

                if event.key == pygame.K_s and mods & pygame.KMOD_CTRL:
                    fname = map_data.name.lower().replace(" ", "_") + "_map.json"
                    map_data.save_json(fname)
                    show_notif(f"Сохранено: {fname}")

                if event.key == pygame.K_e and mods & pygame.KMOD_CTRL:
                    if loaded_from_file:
                        # Мержим в оригинальный файл
                        code_text = PythonMapMerger.merge(loaded_from_file, map_data)
                        show_notif(f"Код с изменениями для {loaded_from_file}")
                    else:
                        code_text = map_data.export_python()
                        show_notif("Новый код сгенерирован")
                    code_scroll = 0
                    mode = "code_view"

                if event.key == pygame.K_w and mods & pygame.KMOD_CTRL:
                    if loaded_from_file:
                        merged = PythonMapMerger.merge(loaded_from_file, map_data)
                        # Бэкап
                        backup = loaded_from_file + ".backup"
                        if os.path.exists(loaded_from_file):
                            import shutil
                            shutil.copy2(loaded_from_file, backup)
                        with open(loaded_from_file, 'w', encoding='utf-8') as f:
                            f.write(merged)
                        show_notif(f"Сохранено в {loaded_from_file} (бэкап: {backup})")
                    else:
                        fname = map_data.name.lower().replace(" ", "_") + "_map.py"
                        code = map_data.export_python()
                        with open(fname, 'w', encoding='utf-8') as f:
                            f.write(code)
                        loaded_from_file = fname
                        show_notif(f"Экспортировано: {fname}")

                if event.key == pygame.K_l and mods & pygame.KMOD_CTRL:
                    # Сканируем файлы
                    available_py_files = sorted([
                        f for f in os.listdir(".")
                        if f.endswith(".py") and f != "location_editor.py"
                           and f != "character_editor.py"
                           and not f.startswith("test_")
                           and not f.startswith("main")
                    ])
                    # Добавляем файлы из game/world/
                    world_dir = os.path.join("game", "world")
                    if os.path.isdir(world_dir):
                        for f in sorted(os.listdir(world_dir)):
                            if f.endswith(".py") and f != "__init__.py":
                                available_py_files.append(os.path.join(world_dir, f))

                    available_json_files = sorted([
                        f for f in os.listdir(".")
                        if f.endswith(".json") and f != "settings.json"
                    ])
                    mode = "load_menu"

                if event.key == pygame.K_r and mods & pygame.KMOD_CTRL:
                    resize_w = str(map_data.width)
                    resize_h = str(map_data.height)
                    resize_name = map_data.name
                    resize_bg_r = str(map_data.bg_color[0])
                    resize_bg_g = str(map_data.bg_color[1])
                    resize_bg_b = str(map_data.bg_color[2])
                    resize_active = "name"
                    mode = "resize"

                if event.key == pygame.K_p and selected_obj:
                    if selected_obj.obj_type in ("transition", "trigger", "npc_spot"):
                        props_target = selected_obj.props.get("target", "")
                        props_label = selected_obj.props.get("label", "")
                        props_active = "target"
                        mode = "props"

                # Перемещение выбранного объекта стрелками
                if selected_obj:
                    step = GRID_SIZE if show_grid else 5
                    if event.key == pygame.K_LEFT:
                        push_undo(); selected_obj.x -= step
                    if event.key == pygame.K_RIGHT:
                        push_undo(); selected_obj.x += step
                    if event.key == pygame.K_UP:
                        push_undo(); selected_obj.y -= step
                    if event.key == pygame.K_DOWN:
                        push_undo(); selected_obj.y += step

            # Масштаб
            if event.type == pygame.MOUSEWHEEL:
                old_zoom = zoom
                zoom *= 1.1 if event.y > 0 else 0.9
                zoom = max(0.2, min(3.0, zoom))

            # Размещение / выбор
            if event.type == pygame.MOUSEBUTTONDOWN:
                on_canvas = mouse[0] > (TOOLBAR_W if show_toolbar else 0)

                if event.button == 1 and on_canvas:
                    if selected_tool:
                        push_undo()
                        obj = MapObject(
                            selected_tool["id"],
                            snap_x, snap_y,
                            selected_tool["size"][0],
                            selected_tool["size"][1],
                            selected_tool["color"],
                            selected_tool.get("solid", False),
                        )
                        map_data.add(obj)
                    else:
                        selected_obj = map_data.get_at(world_mx, world_my)

                elif event.button == 3 and on_canvas:
                    obj = map_data.get_at(world_mx, world_my)
                    if obj:
                        push_undo()
                        map_data.remove(obj)
                        if selected_obj and selected_obj.uid == obj.uid:
                            selected_obj = None

                # Клик на панели инструментов
                if event.button == 1 and show_toolbar and mouse[0] < TOOLBAR_W:
                    # Категории
                    cat_y = 60
                    for cat_name in TOOL_CATEGORIES:
                        r = pygame.Rect(10, cat_y, TOOLBAR_W - 20, 24)
                        if r.collidepoint(mouse):
                            selected_cat = cat_name
                            break
                        cat_y += 28

                    # Инструменты
                    tools = TOOL_CATEGORIES.get(selected_cat, [])
                    tool_y = cat_y + 15
                    for tool in tools:
                        r = pygame.Rect(15, tool_y, TOOLBAR_W - 30, 30)
                        if r.collidepoint(mouse):
                            if selected_tool and selected_tool["id"] == tool["id"]:
                                selected_tool = None  # Снять
                            else:
                                selected_tool = tool
                                selected_obj = None
                            break
                        tool_y += 34

        # ── Движение камеры ──────────────────────────────────────────
        keys = pygame.key.get_pressed()
        cam_speed = 500 / zoom
        if keys[pygame.K_w]: cam_y -= cam_speed * dt
        if keys[pygame.K_s]: cam_y += cam_speed * dt
        if keys[pygame.K_a]: cam_x -= cam_speed * dt
        if keys[pygame.K_d]: cam_x += cam_speed * dt

        # ── Отрисовка ────────────────────────────────────────────────

        screen.blit(bg, (0, 0))

        if mode == "editor":
            canvas_offset = TOOLBAR_W if show_toolbar else 0

            # Карта
            canvas = pygame.Surface((SCREEN_W - canvas_offset, SCREEN_H))
            canvas.fill(map_data.bg_color)

            # Границы карты
            bx = int(-cam_x * zoom)
            by = int(-cam_y * zoom)
            mw = int(map_data.width * zoom)
            mh = int(map_data.height * zoom)
            pygame.draw.rect(canvas, tuple(max(0, c - 10) for c in map_data.bg_color),
                             (bx, by, mw, mh))

            # Сетка
            if show_grid and zoom > 0.3:
                grid_alpha = min(80, int(zoom * 60))
                for gx in range(0, map_data.width, GRID_SIZE):
                    sx = int((gx - cam_x) * zoom)
                    pygame.draw.line(canvas, (255, 255, 255, grid_alpha),
                                     (sx, max(0, by)), (sx, min(SCREEN_H, by + mh)), 1)
                for gy in range(0, map_data.height, GRID_SIZE):
                    sy = int((gy - cam_y) * zoom)
                    pygame.draw.line(canvas, (255, 255, 255, grid_alpha),
                                     (max(0, bx), sy), (min(SCREEN_W, bx + mw), sy), 1)

            # Объекты
            for obj in map_data.objects:
                is_sel = (selected_obj and obj.uid == selected_obj.uid)
                draw_map_object(canvas, obj, cam_x, cam_y, is_sel)

            # Превью размещения
            if selected_tool and mouse[0] > canvas_offset:
                preview = pygame.Surface(
                    (selected_tool["size"][0], selected_tool["size"][1]), pygame.SRCALPHA)
                pygame.draw.rect(preview, (*selected_tool["color"], 120),
                                 preview.get_rect(), border_radius=3)
                pygame.draw.rect(preview, (*selected_tool["color"], 200),
                                 preview.get_rect(), width=2, border_radius=3)
                px = int((snap_x - cam_x) * zoom)
                py = int((snap_y - cam_y) * zoom)
                canvas.blit(preview, (px, py))

            screen.blit(canvas, (canvas_offset, 0))

            # ── Панель инструментов ──────────────────────────────────

            if show_toolbar:
                tb = pygame.Surface((TOOLBAR_W, SCREEN_H), pygame.SRCALPHA)
                pygame.draw.rect(tb, (18, 15, 28, 240), tb.get_rect())
                pygame.draw.line(tb, (*COLOR_PRIMARY_DARK, 150),
                                 (TOOLBAR_W - 1, 0), (TOOLBAR_W - 1, SCREEN_H), 1)

                # Заголовок
                title = font_title.render("Инструменты", True, COLOR_PRIMARY_LIGHT)
                tb.blit(title, (15, 15))

                # Категории
                cat_y = 60
                for cat_name in TOOL_CATEGORIES:
                    is_active = (cat_name == selected_cat)
                    c = COLOR_ACCENT if is_active else COLOR_TEXT_DIM
                    cs = font_heading.render(cat_name, True, c)
                    tb.blit(cs, (15, cat_y + 3))
                    if is_active:
                        pygame.draw.rect(tb, COLOR_ACCENT, (10, cat_y, 3, 20))
                    cat_y += 28

                # Инструменты текущей категории
                tools = TOOL_CATEGORIES.get(selected_cat, [])
                tool_y = cat_y + 15

                for tool in tools:
                    is_sel = (selected_tool and selected_tool["id"] == tool["id"])
                    # Фон
                    r = pygame.Rect(15, tool_y, TOOLBAR_W - 30, 30)
                    if is_sel:
                        pygame.draw.rect(tb, (*COLOR_ACCENT[:3], 40), r, border_radius=5)
                        pygame.draw.rect(tb, COLOR_ACCENT, r, width=2, border_radius=5)
                    # Цвет-образец
                    pygame.draw.rect(tb, tool["color"],
                                     (20, tool_y + 5, 20, 20), border_radius=3)
                    pygame.draw.rect(tb, (80, 70, 90),
                                     (20, tool_y + 5, 20, 20), width=1, border_radius=3)
                    # Название
                    tc = COLOR_ACCENT if is_sel else COLOR_TEXT
                    ts = font_normal.render(tool["name"], True, tc)
                    tb.blit(ts, (48, tool_y + 7))
                    # Размер
                    sz = f"{tool['size'][0]}x{tool['size'][1]}"
                    ss = font_small.render(sz, True, COLOR_TEXT_DIM)
                    tb.blit(ss, (TOOLBAR_W - ss.get_width() - 25, tool_y + 9))

                    tool_y += 34

                screen.blit(tb, (0, 0))

            # ── Нижняя панель ────────────────────────────────────────

            bottom_h = 30
            bottom = pygame.Surface((SCREEN_W, bottom_h), pygame.SRCALPHA)
            pygame.draw.rect(bottom, (15, 12, 25, 230), bottom.get_rect())

            info_parts = [
                f"Карта: {map_data.name} ({map_data.width}x{map_data.height})",
                f"Объектов: {len(map_data.objects)}",
                f"Курсор: ({world_mx}, {world_my})",
                f"Масштаб: {zoom:.1f}x",
            ]
            if loaded_from_file:
                info_parts.append(f"Файл: {loaded_from_file}")
            if selected_obj:
                info_parts.append(f"Выбран: {selected_obj.obj_type} "
                                  f"({selected_obj.x},{selected_obj.y} "
                                  f"{selected_obj.w}x{selected_obj.h})")

            info = "  |  ".join(info_parts)
            bottom.blit(font_small.render(info, True, COLOR_TEXT_DIM), (10, 7))

            shortcuts = "CTRL+S json  CTRL+W сохр.py  CTRL+E код  CTRL+L загр  CTRL+R размер  G сетка  P свойства"
            bottom.blit(font_small.render(shortcuts, True, COLOR_TEXT_DIM),
                        (SCREEN_W - font_small.size(shortcuts)[0] - 10, 7))

            screen.blit(bottom, (0, SCREEN_H - bottom_h))

        # ── Режим просмотра кода ─────────────────────────────────────

        elif mode == "code_view":
            panel = pygame.Surface((SCREEN_W - 40, SCREEN_H - 40), pygame.SRCALPHA)
            pygame.draw.rect(panel, (15, 12, 25, 245), panel.get_rect(), border_radius=12)
            pygame.draw.rect(panel, (*COLOR_PRIMARY_DARK, 180),
                             panel.get_rect(), width=1, border_radius=12)
            screen.blit(panel, (20, 20))

            screen.blit(font_title.render("Экспорт Python-кода", True, COLOR_PRIMARY_LIGHT),
                        (40, 35))
            screen.blit(font_small.render("ESC — назад  |  Колёсико — прокрутка",
                                           True, COLOR_TEXT_DIM), (40, 62))

            lines = code_text.split("\n")
            clip = pygame.Rect(30, 85, SCREEN_W - 60, SCREEN_H - 110)
            old_clip = screen.get_clip()
            screen.set_clip(clip)
            # Кнопка сохранения кода в файл
            save_btn_y = SCREEN_H - 55
            save_btn_r = pygame.Rect(SCREEN_W // 2 - 200, save_btn_y, 180, 38)
            pygame.draw.rect(screen, (35, 55, 35), save_btn_r, border_radius=8)
            pygame.draw.rect(screen, COLOR_SUCCESS, save_btn_r, width=2, border_radius=8)
            screen.blit(font_btn.render("Сохранить в файл", True, COLOR_SUCCESS),
                        (save_btn_r.x + 20, save_btn_r.y + 9))

            close_btn_r = pygame.Rect(SCREEN_W // 2 + 20, save_btn_y, 180, 38)
            pygame.draw.rect(screen, (55, 35, 35), close_btn_r, border_radius=8)
            pygame.draw.rect(screen, COLOR_DANGER, close_btn_r, width=2, border_radius=8)
            screen.blit(font_btn.render("Закрыть (ESC)", True, COLOR_DANGER),
                        (close_btn_r.x + 25, close_btn_r.y + 9))

            # Информация
            if loaded_from_file:
                info_s = font_small.render(
                    f"Исходный файл: {loaded_from_file}  |  "
                    f"Изменения будут добавлены в оригинал",
                    True, COLOR_ACCENT)
            else:
                info_s = font_small.render(
                    "Новый файл  |  Будет создан с нуля", True, COLOR_TEXT_DIM)
            screen.blit(info_s, (40, 65))

            for i, line in enumerate(lines):
                ly = 90 + (i - code_scroll) * 16
                if ly < 75 or ly > SCREEN_H - 30:
                    continue
                color = (180, 180, 190)
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("#"):
                    color = (100, 160, 100)
                elif stripped.startswith("MAP_") or stripped.startswith("SPAWN"):
                    color = (120, 180, 255)
                elif any(stripped.startswith(k) for k in ["ROADS","TERRAIN","TREES",
                         "ROCKS","FLOWERS","BUILDINGS","FURNITURE","ZONES","COLLIDERS",
                         "TRANSITIONS"]):
                    color = (200, 170, 120)
                screen.blit(font_code.render(f"{i+1:4d}  {line}", True, color), (40, ly))
            screen.set_clip(old_clip)

        # ── Меню загрузки ────────────────────────────────────────────

        elif mode == "load_menu":

            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

            overlay.fill((0, 0, 0, 180))

            screen.blit(overlay, (0, 0))

            menu_x = SCREEN_W // 2 - 220

            menu_y = 120

            # Высота панели

            total_items = 1 + len(PRESETS) + len(available_py_files) + len(available_json_files)

            panel_h = min(SCREEN_H - 100, total_items * 45 + 200)

            panel = pygame.Surface((440, panel_h), pygame.SRCALPHA)

            pygame.draw.rect(panel, (20, 18, 32, 245), panel.get_rect(), border_radius=14)

            pygame.draw.rect(panel, (*COLOR_PRIMARY_DARK, 180),

                             panel.get_rect(), width=1, border_radius=14)

            screen.blit(panel, (menu_x, menu_y))

            screen.blit(font_title.render("Загрузить / Создать", True, COLOR_PRIMARY_LIGHT),

                        (menu_x + 20, menu_y + 15))

            # Новая карта

            pygame.draw.rect(screen, (35, 55, 35),

                             (menu_x + 10, menu_y + 55, 420, 38), border_radius=6)

            pygame.draw.rect(screen, COLOR_SUCCESS,

                             (menu_x + 10, menu_y + 55, 420, 38), width=1, border_radius=6)

            screen.blit(font_btn.render("+ Новая пустая карта", True, COLOR_SUCCESS),

                        (menu_x + 30, menu_y + 64))

            # Пресеты

            screen.blit(font_heading.render("Встроенные локации:", True, COLOR_TEXT_DIM),

                        (menu_x + 15, menu_y + 100))

            for i, (key, (pname, _)) in enumerate(PRESETS.items()):
                by = menu_y + 120 + i * 48

                pygame.draw.rect(screen, (35, 30, 50),

                                 (menu_x + 10, by, 420, 38), border_radius=6)

                pygame.draw.rect(screen, COLOR_PRIMARY_DARK,

                                 (menu_x + 10, by, 420, 38), width=1, border_radius=6)

                screen.blit(font_btn.render(f"📦  {pname}", True, COLOR_TEXT),

                            (menu_x + 25, by + 9))

            # Python файлы

            py_start_y = menu_y + 120 + len(PRESETS) * 48 + 20

            if available_py_files:
                screen.blit(font_heading.render("Python файлы (.py):", True, COLOR_TEXT_DIM),

                            (menu_x + 15, py_start_y - 18))

            for fi, py_file in enumerate(available_py_files):

                fy = py_start_y + fi * 40

                if fy + 34 > menu_y + panel_h:
                    break

                is_loaded = (loaded_from_file == py_file)

                bg_col = (45, 40, 60) if is_loaded else (30, 28, 45)

                border = COLOR_ACCENT if is_loaded else (60, 50, 80)

                pygame.draw.rect(screen, bg_col,

                                 (menu_x + 10, fy, 420, 34), border_radius=5)

                pygame.draw.rect(screen, border,

                                 (menu_x + 10, fy, 420, 34), width=1, border_radius=5)

                # Иконка

                icon_color = COLOR_ACCENT if is_loaded else (200, 170, 100)

                screen.blit(font_small.render("🐍", True, icon_color), (menu_x + 18, fy + 7))

                # Имя файла

                display_name = py_file

                if len(display_name) > 40:
                    display_name = "..." + display_name[-37:]

                name_col = COLOR_ACCENT if is_loaded else COLOR_TEXT

                screen.blit(font_normal.render(display_name, True, name_col),

                            (menu_x + 42, fy + 8))

                if is_loaded:
                    screen.blit(font_small.render("(текущий)", True, COLOR_ACCENT),

                                (menu_x + 360, fy + 10))

            # JSON файлы

            json_start_y = py_start_y + len(available_py_files) * 40 + 20

            if available_json_files:

                if json_start_y - 18 < menu_y + panel_h - 30:
                    screen.blit(font_heading.render("JSON файлы:", True, COLOR_TEXT_DIM),

                                (menu_x + 15, json_start_y - 18))

            for fi, json_file in enumerate(available_json_files):

                fy = json_start_y + fi * 40

                if fy + 34 > menu_y + panel_h:
                    break

                pygame.draw.rect(screen, (30, 35, 45),

                                 (menu_x + 10, fy, 420, 34), border_radius=5)

                pygame.draw.rect(screen, (50, 70, 90),

                                 (menu_x + 10, fy, 420, 34), width=1, border_radius=5)

                screen.blit(font_normal.render(f"📄  {json_file}", True, COLOR_TEXT),

                            (menu_x + 25, fy + 8))

            # Подсказка

            screen.blit(font_small.render(

                "ESC — отмена  |  Клик — загрузить", True, COLOR_TEXT_DIM),

                (menu_x + 100, menu_y + panel_h - 22))

        # ── Диалог изменения размера ─────────────────────────────────

        elif mode == "resize":
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            dx = SCREEN_W // 2 - 150
            dy = 200
            panel = pygame.Surface((300, 260), pygame.SRCALPHA)
            pygame.draw.rect(panel, (20, 18, 32, 240), panel.get_rect(), border_radius=12)
            screen.blit(panel, (dx, dy - 30))

            screen.blit(font_title.render("Параметры карты", True, COLOR_PRIMARY_LIGHT),
                        (dx + 20, dy - 20))

            def draw_field(label, value, fy, field_id):
                screen.blit(font_normal.render(label, True, COLOR_TEXT), (dx + 10, fy + 4))
                active = resize_active == field_id
                bc = COLOR_ACCENT if active else COLOR_PRIMARY_DARK
                pygame.draw.rect(screen, (35, 30, 50), (dx + 80, fy, 200, 26), border_radius=5)
                pygame.draw.rect(screen, bc, (dx + 80, fy, 200, 26), width=1, border_radius=5)
                screen.blit(font_normal.render(value, True, COLOR_TEXT), (dx + 88, fy + 4))

            draw_field("Имя:", resize_name, dy + 30, "name")
            draw_field("Ширина:", resize_w, dy + 85, "w")
            draw_field("Высота:", resize_h, dy + 140, "h")

            screen.blit(font_normal.render("Фон RGB:", True, COLOR_TEXT), (dx + 10, dy + 195))
            for ci, (cv, cid, cl) in enumerate([
                (resize_bg_r, "r", "R"), (resize_bg_g, "g", "G"), (resize_bg_b, "b", "B")
            ]):
                fx = dx + 80 + ci * 70
                active = resize_active == cid
                bc = COLOR_ACCENT if active else COLOR_PRIMARY_DARK
                pygame.draw.rect(screen, (35, 30, 50), (fx, dy + 195, 60, 24), border_radius=4)
                pygame.draw.rect(screen, bc, (fx, dy + 195, 60, 24), width=1, border_radius=4)
                screen.blit(font_small.render(f"{cl}:{cv}", True, COLOR_TEXT), (fx + 4, dy + 199))

            screen.blit(font_small.render("ENTER — применить  |  ESC — отмена",
                                           True, COLOR_TEXT_DIM), (dx + 20, dy + 225))

        # ── Свойства объекта ─────────────────────────────────────────

        elif mode == "props":
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            dx = SCREEN_W // 2 - 150
            dy = 230
            panel = pygame.Surface((300, 160), pygame.SRCALPHA)
            pygame.draw.rect(panel, (20, 18, 32, 240), panel.get_rect(), border_radius=12)
            screen.blit(panel, (dx, dy - 20))

            screen.blit(font_title.render("Свойства", True, COLOR_PRIMARY_LIGHT),
                        (dx + 20, dy - 10))

            for label, value, fy, fid in [
                ("Цель:", props_target, dy + 30, "target"),
                ("Метка:", props_label, dy + 80, "label"),
            ]:
                screen.blit(font_normal.render(label, True, COLOR_TEXT), (dx + 10, fy + 4))
                active = props_active == fid
                bc = COLOR_ACCENT if active else COLOR_PRIMARY_DARK
                pygame.draw.rect(screen, (35, 30, 50), (dx + 80, fy, 200, 26), border_radius=5)
                pygame.draw.rect(screen, bc, (dx + 80, fy, 200, 26), width=1, border_radius=5)
                screen.blit(font_normal.render(value, True, COLOR_TEXT), (dx + 88, fy + 4))

            screen.blit(font_small.render("ENTER — сохранить  |  TAB — переключить",
                                           True, COLOR_TEXT_DIM), (dx + 15, dy + 120))

        # ── Уведомление ──────────────────────────────────────────────

        if notif_timer > 0 and notification:
            alpha = min(255, int(notif_timer * 3 * 255))
            ns = font_heading.render(notification, True, COLOR_ACCENT)
            nbg = pygame.Surface((ns.get_width() + 30, 30), pygame.SRCALPHA)
            pygame.draw.rect(nbg, (20, 18, 32, min(alpha, 220)),
                             nbg.get_rect(), border_radius=6)
            screen.blit(nbg, (SCREEN_W // 2 - nbg.get_width() // 2, 10))
            ns.set_alpha(alpha)
            screen.blit(ns, (SCREEN_W // 2 - ns.get_width() // 2, 15))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()