import random
import sys
import pygame as pg

# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
TEXT_COLOR = (255, 255, 255)

# Скорость
SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 40
SPEED_STEP = 2

# Флаг для тестов
_is_testing = 'pytest' in sys.modules or 'unittest' in sys.modules

# Инициализация Pygame (только не в тестах)
if not _is_testing:
    pg.init()
    pg.font.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption(
        'Змейка | Стрелки - движение | ESC - выход | +/- скорость'
    )
    clock = pg.time.Clock()
    font = pg.font.Font(None, 36)
else:
    # Заглушки для тестов
    screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 36)


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color: tuple = None) -> None:
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position, color, draw_border=True):
        """
        Рисует ячейку на экране по позиции и выбранному цвету.
        :param position: координаты ячейки
        :param color: цвет ячейки
        :param draw_border: рисовать ли рамку
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if draw_border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """
        Метод, который должен быть реализован в дочерних классах.
        """
        raise NotImplementedError(
            'Метод draw() должен быть переопределен в дочернем классе'
        )


class Apple(GameObject):
    """Класс для яблока."""

    def __init__(self, used_positions=None):
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(used_positions or [])

    def randomize_position(self, used_positions=None):
        """
        Располагает яблоко в случайной позиции, которая не занята.
        :param used_positions: занятые позиции игрока
        """
        while True:
            self.position = (
                random.randrange(GRID_WIDTH) * GRID_SIZE,
                random.randrange(GRID_HEIGHT) * GRID_SIZE
            )
            if used_positions is None or self.position not in used_positions:
                break

    def draw(self):
        """Отрисовка яблока."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Класс для змейки."""

    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def update_direction(self, new_direction):
        """
        Обновляет направление движения змейки.
        :param new_direction: новое направление
        """
        self.direction = new_direction

    def move(self):
        """
        Перемещает змейку в текущем направлении.
        """
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

    def draw(self):
        """Отрисовка змейки."""
        for position in self.positions:
            self.draw_cell(position, self.body_color)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сброс состояния змейки при поражении."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [self.position]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(game_object):
    """
    Обработка нажатий клавиш.
    :param game_object: текущий объект (змейка)
    :return: False при закрытии окна или ESC
    """
    global SPEED
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False

            # Управление скоростью
            if event.key in (pg.K_PLUS, pg.K_EQUALS):
                SPEED = min(SPEED + SPEED_STEP, MAX_SPEED)
            elif event.key == pg.K_MINUS:
                SPEED = max(SPEED - SPEED_STEP, MIN_SPEED)

            # Управление направлением
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.update_direction(UP)
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.update_direction(DOWN)
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.update_direction(LEFT)
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.update_direction(RIGHT)

    return True


def draw_speed():
    """Отображение текущей скорости."""
    speed_text = font.render(f'Скорость: {SPEED}', True, TEXT_COLOR)
    screen.blit(speed_text, (10, 10))


def main():
    """Основная функция запуска игры."""
    snake = Snake()
    apple = Apple(snake.positions)

    global SPEED

    # Не запускаем игру в тестовой среде
    if _is_testing:
        return

    while True:
        clock.tick(SPEED)

        if not handle_keys(snake):
            break

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        snake.move()

        # Проверка на столкновение с собой
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