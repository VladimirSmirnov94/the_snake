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

# Инициализация Pygame
pg.init()
pg.font.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Змейка | ESC - выход | +/- скорость')
clock = pg.time.Clock()
font = pg.font.Font(None, 36)


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw_cell(self, position, color, draw_border=True):
        """Отрисовывает ячейку по позиции и цвету."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if draw_border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Абстрактный метод для отрисовки."""
        raise NotImplementedError(
            'Метод draw() должен быть переопределен в дочернем классе'
        )


class Apple(GameObject):
    """Класс для яблока."""

    def __init__(self, used_positions=None):
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(used_positions or [])

    def randomize_position(self, used_positions=None):
        """Располагает яблоко в случайной позиции."""
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
        self.reset()
        self.direction = RIGHT

    def update_direction(self, new_direction):
        """Обновляет направление движения."""
        self.direction = new_direction

    def move(self):
        """Перемещает змейку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        self.position = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, self.position)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовка змейки."""
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, False)
        for position in self.positions:
            self.draw_cell(position, self.body_color)

    def get_head_position(self):
        """Возвращает позицию головы."""
        return self.positions[0]

    def reset(self):
        """Сброс состояния змейки."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [self.position]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def _change_speed(event):
    """Изменяет скорость игры."""
    global SPEED
    if event.key in (pg.K_PLUS, pg.K_EQUALS):
        SPEED = min(SPEED + SPEED_STEP, MAX_SPEED)
        return True
    if event.key == pg.K_MINUS:
        SPEED = max(SPEED - SPEED_STEP, MIN_SPEED)
        return True
    return False


def _change_direction(event, snake):
    """Изменяет направление движения змейки."""
    key = event.key
    direction = snake.direction
    if key == pg.K_UP and direction != DOWN:
        snake.update_direction(UP)
    elif key == pg.K_DOWN and direction != UP:
        snake.update_direction(DOWN)
    elif key == pg.K_LEFT and direction != RIGHT:
        snake.update_direction(LEFT)
    elif key == pg.K_RIGHT and direction != LEFT:
        snake.update_direction(RIGHT)


def handle_keys(snake):
    """Обработка событий клавиш. Возвращает False при выходе."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        if event.type != pg.KEYDOWN:
            continue
        if event.key == pg.K_ESCAPE:
            return False
        if _change_speed(event):
            continue
        _change_direction(event, snake)
    return True


def draw_speed():
    """Отображение текущей скорости на экране."""
    speed_text = font.render(f'Скорость: {SPEED}', True, TEXT_COLOR)
    screen.blit(speed_text, (10, 10))


def main():
    """Основной цикл игры."""

    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        # Обработка клавиш
        if not handle_keys(snake):
            break

        # Движение змейки
        snake.move()

        # Получаем позицию головы
        head = snake.get_head_position()
        body = snake.positions[1:]  # тело без головы

        # Проверка столкновения с собой
        if head in body:
            snake.reset()
            # очистить экран при столкновении
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
            continue  # пропускаем остальную логику этого кадра

        # Проверяем, съела ли змейка яблоко
        if head == apple.position:
            snake.length += 1  # увеличиваем длину змейки
            apple.randomize_position(snake.positions)  # ставим новое яблоко

        # Отрисовка
        if snake.last:  # Затираем последнюю ячейку, если хвост сдвинулся
            GameObject().draw_cell(snake.last, BOARD_BACKGROUND_COLOR, False)
        apple.draw()
        snake.draw()
        draw_speed()
        pg.display.update()

    pg.quit()


if __name__ == '__main__':
    main()
