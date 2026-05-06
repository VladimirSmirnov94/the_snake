import random

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет текста
TEXT_COLOR = (255, 255, 255)

# Скорость движения змейки (начальная):
SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 40
SPEED_STEP = 2

# Инициализация PyGame:
pg.init()
pg.font.init()

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка | ESC - выход')

# Настройка времени:
clock = pg.time.Clock()

# Шрифт для отображения скорости
font = pg.font.Font(None, 36)


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color: tuple = None) -> None:
        """Инициализирует базовый игровой объект."""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = body_color

    def draw_cell(self, position, color, draw_border=True):
        """Отрисовывает отдельную ячейку на игровом поле."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if draw_border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self) -> None:
        """Абстрактный метод для отрисовки объекта."""
        raise NotImplementedError(
            'Метод draw() должен быть переопределен в дочернем классе'
        )


class Apple(GameObject):
    """Класс яблока, которое появляется на игровом поле."""

    def __init__(self, used_positions=None):
        """Инициализирует яблоко и задаёт его случайную позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(used_positions or [])

    def randomize_position(self, used_positions: list = None) -> None:
        """Устанавливает яблоку случайную позицию."""
        while True:
            self.position = (
                random.randrange(GRID_WIDTH) * GRID_SIZE,
                random.randrange(GRID_HEIGHT) * GRID_SIZE
            )
            if used_positions is None or self.position not in used_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    def __init__(self):
        """Инициализирует змейку в начальном состоянии."""
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 2
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки."""
        self.direction = new_direction

    def move(self):
        """Перемещает змейку на одну ячейку."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self) -> None:
        """Отрисовывает только голову змейки."""
        head_pos = self.get_head_position()
        self.draw_cell(head_pos, self.body_color)

        if self.last:
            self.draw_cell(
                self.last, BOARD_BACKGROUND_COLOR, draw_border=False
            )

    def get_head_position(self) -> tuple:
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [self.position]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш."""
    global SPEED

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_ESCAPE:
            return False

        speed_keys = {
            pg.K_PLUS: SPEED + SPEED_STEP,
            pg.K_EQUALS: SPEED + SPEED_STEP,
            pg.K_MINUS: SPEED - SPEED_STEP,
        }

        if event.key in speed_keys:
            if event.key == pg.K_MINUS:
                SPEED = max(speed_keys[event.key], MIN_SPEED)
            else:
                SPEED = min(speed_keys[event.key], MAX_SPEED)
            return True

        direction_map = {
            (pg.K_UP, DOWN): UP,
            (pg.K_DOWN, UP): DOWN,
            (pg.K_LEFT, RIGHT): LEFT,
            (pg.K_RIGHT, LEFT): RIGHT,
        }

        new_direction = direction_map.get(
            (event.key, game_object.direction)
        )
        if new_direction:
            game_object.update_direction(new_direction)

    return True


def draw_speed():
    """Отображает текущую скорость на экране."""
    speed_text = font.render(f'Скорость: {SPEED}', True, TEXT_COLOR)
    screen.blit(speed_text, (10, 10))


def main():
    """Основная функция игры с главным игровым циклом."""
    snake = Snake()
    apple = Apple(snake.positions)

    global SPEED

    screen.fill(BOARD_BACKGROUND_COLOR)
    apple.draw()
    snake.draw()
    draw_speed()
    pg.display.update()

    while True:
        clock.tick(SPEED)

        if not handle_keys(snake):
            break

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        draw_speed()
        pg.display.update()

    pg.quit()


if __name__ == '__main__':
    main()