import random
from random import randint, uniform
from enum import Enum, auto

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.vector import Vector
from kivy.core.audio import SoundLoader


# ============================================================
#                        PONG GAME
# ============================================================

class PongGame(Widget):
    def __init__(self, ai_difficulty=5,
                 paddle_color=(1, 1, 1),
                 ball_color=(1, 1, 1),
                 high_score=0,
                 **kwargs):
        super().__init__(**kwargs)

        self.ai_difficulty = ai_difficulty
        self.ball_speed_multiplier = 1.1
        self.ball_color = ball_color
        self.paddle_color = paddle_color

        # Ball state
        self.ball_size = 20
        self.ball_x = Window.width / 2
        self.ball_y = Window.height / 2
        self.ball_dx = random.choice([-4, -3, 3, 4])
        self.ball_dy = random.choice([-4, -3, 3, 4])

        # Player paddle (bottom)
        self.paddle_width = 100
        self.paddle_height = 20
        self.player_y = 20
        self.player_x = Window.width / 2 - self.paddle_width / 2
        self.player_move_speed = 8  # for keyboard control

        # AI paddle (top)
        self.ai_y = Window.height - 20
        self.ai_x = Window.width / 2 - self.paddle_width / 2

        # Scores
        self.player_score = 0
        self.ai_score = 0
        self.high_score = high_score
        self.win_score = 10

        # Keyboard state (for left/right arrows)
        self.key_left_pressed = False
        self.key_right_pressed = False

        # Return to Menu Button
        self.menu_button = Button(
            text="Return to Menu",
            size_hint=(0.2, 0.1),
            pos_hint={'x': 0, 'y': 0.9}
        )
        self.menu_button.bind(on_release=self.return_to_menu)
        self.add_widget(self.menu_button)

        # Labels
        self.score_label1 = Label(
            text=f"Player: {self.player_score}",
            font_size=24,
            pos=(Window.width * 0.1, Window.height - 60),
            size_hint=(None, None)
        )
        self.score_label2 = Label(
            text=f"AI: {self.ai_score}",
            font_size=24,
            pos=(Window.width * 0.7, Window.height - 60),
            size_hint=(None, None)
        )
        self.high_score_label = Label(
            text=f"High Score: {self.high_score}",
            font_size=24,
            pos=(Window.width * 0.4, Window.height - 60),
            size_hint=(None, None)
        )

        self.add_widget(self.score_label1)
        self.add_widget(self.score_label2)
        self.add_widget(self.high_score_label)

        with self.canvas:
            # Ball
            Color(*self.ball_color)
            self.ball = Ellipse(pos=(self.ball_x, self.ball_y),
                                size=(self.ball_size, self.ball_size))

            # Player paddle
            Color(*self.paddle_color)
            self.player = Line(points=[
                self.player_x, self.player_y,
                self.player_x + self.paddle_width, self.player_y
            ], width=10)

            # AI paddle
            self.ai = Line(points=[
                self.ai_x, self.ai_y,
                self.ai_x + self.paddle_width, self.ai_y
            ], width=10)

            # Center line
            Color(1, 1, 1, 1)
            self.center_line = Line(points=[
                0, Window.height / 2,
                Window.width, Window.height / 2
            ], width=2)

        # Schedule game loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        # Bind keys for arrow control
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

    def reset_ball(self):
        self.ball_x = Window.width / 2
        self.ball_y = Window.height / 2
        self.ball_dx = random.choice([-4, -3, 3, 4])
        self.ball_dy = random.choice([-4, -3, 3, 4])
        self.ball.pos = (self.ball_x, self.ball_y)

    def on_touch_move(self, touch):
        if touch.y < Window.height / 2:
            self.player_x = max(
                0,
                min(Window.width - self.paddle_width,
                    touch.x - self.paddle_width / 2)
            )
            self.player.points = [
                self.player_x, self.player_y,
                self.player_x + self.paddle_width, self.player_y
            ]

    def on_key_down(self, window, keycode, scancode, text, modifiers):
        if keycode == 275:  # Right arrow
            self.key_right_pressed = True
        elif keycode == 276:  # Left arrow
            self.key_left_pressed = True

    def on_key_up(self, window, keycode, scancode):
        if keycode == 275:  # Right arrow
            self.key_right_pressed = False
        elif keycode == 276:  # Left arrow
            self.key_left_pressed = False

    def update(self, dt):
        # Keyboard movement for player
        if self.key_left_pressed:
            self.player_x -= self.player_move_speed
        if self.key_right_pressed:
            self.player_x += self.player_move_speed
        self.player_x = max(0, min(Window.width - self.paddle_width, self.player_x))
        self.player.points = [
            self.player_x, self.player_y,
            self.player_x + self.paddle_width, self.player_y
        ]

        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Vertical walls
        if self.ball_x <= 0 or self.ball_x >= Window.width - self.ball_size:
            self.ball_dx *= -1

        # Player paddle collision
        if (self.ball_y <= self.player_y + self.paddle_height and
                self.player_x <= self.ball_x <= self.player_x + self.paddle_width and
                self.ball_dy < 0):
            self.ball_dy *= -1
            self.accelerate_ball()

        # AI paddle collision
        if (self.ball_y + self.ball_size >= self.ai_y - self.paddle_height and
                self.ai_x <= self.ball_x <= self.ai_x + self.paddle_width and
                self.ball_dy > 0):
            self.ball_dy *= -1
            self.accelerate_ball()

        # AI movement: follow ball horizontally
        if self.ball_x > self.ai_x + self.paddle_width / 2:
            self.ai_x += self.ai_difficulty
        elif self.ball_x < self.ai_x + self.paddle_width / 2:
            self.ai_x -= self.ai_difficulty

        # Clamp AI paddle
        self.ai_x = max(0, min(Window.width - self.paddle_width, self.ai_x))

        # Update AI paddle line
        self.ai.points = [
            self.ai_x, self.ai_y,
            self.ai_x + self.paddle_width, self.ai_y
        ]

        # Scoring: missed top/bottom
        if self.ball_y <= 0:
            # AI scores
            self.ai_score += 1
            self.score_label2.text = f"AI: {self.ai_score}"
            self.reset_ball()
            self.check_win_condition()
        elif self.ball_y >= Window.height:
            # Player scores
            self.player_score += 1
            self.score_label1.text = f"Player: {self.player_score}"
            self.reset_ball()
            self.check_win_condition()

        # Update ball graphic
        self.ball.pos = (self.ball_x, self.ball_y)

        # High score
        self.update_high_score()

    def accelerate_ball(self):
        self.ball_dx *= self.ball_speed_multiplier
        self.ball_dy *= self.ball_speed_multiplier

    def update_high_score(self):
        if self.player_score > self.high_score:
            self.high_score = self.player_score
            self.high_score_label.text = f"High Score: {self.high_score}"

    def check_win_condition(self):
        if self.player_score >= self.win_score:
            self.show_popup("You Win!")
        elif self.ai_score >= self.win_score:
            self.show_popup("You've been defeated!")

    def show_popup(self, message):
        layout = BoxLayout(orientation='vertical', padding=10)
        label = Label(text=message, font_size=24)
        close_button = Button(text="Return to Menu", size_hint=(1, 0.2))

        layout.add_widget(label)
        layout.add_widget(close_button)

        popup = Popup(title="Game Over",
                      content=layout,
                      size_hint=(0.6, 0.4))

        close_button.bind(on_release=popup.dismiss)
        popup.bind(on_dismiss=self.return_to_menu)
        popup.open()

    def return_to_menu(self, instance=None):
        Clock.unschedule(self.update)
        Window.unbind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(LaunchMenu())

# ============================================================
#                     BRICK BREAK GAME
# ============================================================

FPS = 1.0 / 144.0
BALL_SIZE = (20, 20)
PADDLE_SIZE = (100, 20)
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_HEIGHT = 20
BALL_SPEED_MULTIPLIER = 1.05

class BrickBall:
    def __init__(self, game):
        self.game = game
        self.reset()
        with game.canvas:
            Color(1, 1, 1)
            self.shape = Ellipse(pos=(self.x, self.y), size=BALL_SIZE)

    def reset(self):
        self.x = Window.width / 2
        self.y = 100
        self.dx = randint(-5, 5) or 1
        self.dy = 5

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.shape.pos = (self.x, self.y)

    def bounce_x(self):
        self.dx *= -1

    def bounce_y(self):
        self.dy *= -1

    def increase_speed(self):
        self.dx *= BALL_SPEED_MULTIPLIER
        self.dy *= BALL_SPEED_MULTIPLIER

class BrickPaddle:
    def __init__(self, game):
        self.game = game
        self.width, self.height = PADDLE_SIZE
        self.x = Window.width / 2 - self.width / 2
        self.y = 20
        self.move_speed = 10
        with game.canvas:
            Color(1, 1, 1)
            self.shape = Rectangle(pos=(self.x, self.y), size=PADDLE_SIZE)

    def update_position(self, x):
        self.x = max(0, min(Window.width - self.width, x - self.width / 2))
        self.shape.pos = (self.x, self.y)

    def move_left(self):
        self.x = max(0, self.x - self.move_speed)
        self.shape.pos = (self.x, self.y)

    def move_right(self):
        self.x = min(Window.width - self.width, self.x + self.move_speed)
        self.shape.pos = (self.x, self.y)

class Brick:
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos
        with game.canvas:
            Color(1, 0, 0)
            self.shape = Rectangle(pos=self.pos,
                                   size=(game.brick_width, BRICK_HEIGHT))

class BrickBreakGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.brick_width = Window.width / BRICK_COLS
        self.score = 0
        self.lives = 3
        self.bricks = []
        self.lives_label = None

        # Keyboard state
        self.key_left_pressed = False
        self.key_right_pressed = False

        self.init_game()
        Clock.schedule_interval(self.update, FPS)
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

    def init_game(self):
        self.canvas.clear()
        self.score = 0
        if self.lives <= 0:
            self.lives = 3

        self.ball = BrickBall(self)
        self.paddle = BrickPaddle(self)
        self.create_bricks()

        if self.lives_label:
            self.remove_widget(self.lives_label)
        self.lives_label = Label(
            text=f"Lives: {self.lives}",
            font_size=24,
            size_hint=(0.2, 0.1),
            pos_hint={'x': 0, 'y': 0.95}
        )
        self.add_widget(self.lives_label)

    def create_bricks(self):
        self.bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                brick = Brick(
                    self,
                    (col * self.brick_width,
                     Window.height - (row + 1) * BRICK_HEIGHT)
                )
                self.bricks.append(brick)

    def on_key_down(self, window, keycode, scancode, text, modifiers):
        if keycode == 275:  # right
            self.key_right_pressed = True
        elif keycode == 276:  # left
            self.key_left_pressed = True

    def on_key_up(self, window, keycode, scancode):
        if keycode == 275:
            self.key_right_pressed = False
        elif keycode == 276:
            self.key_left_pressed = False

    def update(self, dt):
        # Keyboard movement
        if self.key_left_pressed:
            self.paddle.move_left()
        if self.key_right_pressed:
            self.paddle.move_right()

        self.ball.move()
        self.handle_collisions()
        self.check_ball_out_of_bounds()
        self.update_ui()

    def handle_collisions(self):
        if self.ball.x <= 0 or self.ball.x >= Window.width - BALL_SIZE[0]:
            self.ball.bounce_x()
        if self.ball.y >= Window.height - BALL_SIZE[1]:
            self.ball.bounce_y()

        # Paddle collision
        if (self.paddle.x <= self.ball.x + BALL_SIZE[0] <= self.paddle.x + PADDLE_SIZE[0] and
                self.paddle.y <= self.ball.y <= self.paddle.y + PADDLE_SIZE[1]):
            self.ball.bounce_y()
            self.ball.increase_speed()
            self.animate_ball_bounce()

        # Bricks
        for brick in self.bricks[:]:
            bx, by = brick.shape.pos
            if (bx <= self.ball.x + BALL_SIZE[0] <= bx + self.brick_width and
                    by <= self.ball.y + BALL_SIZE[1] <= by + BRICK_HEIGHT):
                self.ball.bounce_y()
                self.score += 1
                self.animate_brick_destruction(brick)
                self.bricks.remove(brick)
                break

        if not self.bricks:
            self.reset_game("You Win!")

    def check_ball_out_of_bounds(self):
        if self.ball.y <= 0:
            self.lives -= 1
            self.lives_label.text = f"Lives: {self.lives}"
            if self.lives <= 0:
                self.reset_game("Game Over!")
            else:
                self.ball.reset()

    def reset_game(self, message):
        Clock.unschedule(self.update)
        if message == "Game Over!":
            self.show_popup(message)
        else:
            self.lives = 3
            self.init_game()
            Clock.schedule_interval(self.update, FPS)

    def on_touch_move(self, touch):
        if touch.y < Window.height / 3:
            self.paddle.update_position(touch.x)

    def animate_ball_bounce(self):
        anim = Animation(size=(30, 30), duration=0.1) + Animation(
            size=BALL_SIZE, duration=0.1)
        anim.start(self.ball.shape)

    def animate_brick_destruction(self, brick):
        anim = (Animation(size=(0, 0), duration=0.1) +
                Animation(size=(self.brick_width, BRICK_HEIGHT), duration=0.1))
        anim.start(brick.shape)
        anim.bind(on_complete=lambda *args: self.canvas.remove(brick.shape))

    def show_popup(self, message):
        layout = BoxLayout(orientation='vertical', padding=10)
        label = Label(text=message, font_size=24)
        restart_button = Button(text="Restart", size_hint=(1, 0.2))
        close_button = Button(text="Return to Menu", size_hint=(1, 0.2))

        layout.add_widget(label)
        layout.add_widget(restart_button)
        layout.add_widget(close_button)

        popup = Popup(title=message, content=layout, size_hint=(0.6, 0.4))

        restart_button.bind(
            on_release=lambda *args: self._restart_from_popup(popup))
        close_button.bind(
            on_release=lambda *args: self.return_to_menu(popup))

        popup.open()

    def _restart_from_popup(self, popup):
        popup.dismiss()
        self.lives = 3
        self.init_game()
        Clock.schedule_interval(self.update, FPS)

    def return_to_menu(self, popup):
        Clock.unschedule(self.update)
        Window.unbind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        app = App.get_running_app()
        app.root.clear_widgets()
        popup.dismiss()
        app.root.add_widget(LaunchMenu())

    def update_ui(self):
        self.lives_label.text = f"Lives: {self.lives}"

# ============================================================
#                        SNAKE GAME
# ============================================================

SNAKE_FPS = 1.0 / 10.0

class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Snake state
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.snake_direction = 'RIGHT'
        self.block_size = 20
        self.wall_thickness = 20
        self.food = self.generate_food_position()
        self.game_over = False
        self.score = 0

        # Score label
        self.score_label = Label(
            text=f"Score: {self.score}",
            font_size=24,
            size_hint=(0.2, 0.1),
            pos_hint={'x': 0, 'y': 0.9}
        )
        self.add_widget(self.score_label)

        # Game loop
        Clock.schedule_interval(self.update, SNAKE_FPS)

        # Keyboard input
        Window.bind(on_key_down=self.on_key_down)

    def on_key_down(self, window, keycode, scancode, text, modifiers):
        if keycode == 275 and self.snake_direction != 'LEFT':   # Right
            self.snake_direction = 'RIGHT'
        elif keycode == 276 and self.snake_direction != 'RIGHT':  # Left
            self.snake_direction = 'LEFT'
        elif keycode == 273 and self.snake_direction != 'DOWN':   # Up
            self.snake_direction = 'UP'
        elif keycode == 274 and self.snake_direction != 'UP':     # Down
            self.snake_direction = 'DOWN'

    def move_snake(self):
        x, y = self.snake[0]
        if self.snake_direction == 'RIGHT':
            new_head = (x + self.block_size, y)
        elif self.snake_direction == 'LEFT':
            new_head = (x - self.block_size, y)
        elif self.snake_direction == 'UP':
            new_head = (x, y + self.block_size)
        else:  # DOWN
            new_head = (x, y - self.block_size)

        # Move snake by inserting new head and dropping last segment
        self.snake = [new_head] + self.snake[:-1]

    def check_collision(self):
        head = self.snake[0]
        # Wall collisions (boundaries)
        if not (self.wall_thickness <= head[0] < Window.width - self.wall_thickness and
                self.wall_thickness <= head[1] < Window.height - self.wall_thickness):
            self.game_over = True

        # Self-collision
        if head in self.snake[1:]:
            self.game_over = True

    def check_food_collision(self):
        if self.snake[0] == self.food:
            # Grow snake
            self.snake.append(self.snake[-1])
            self.food = self.generate_food_position()
            self.score += 1
            self.score_label.text = f"Score: {self.score}"

    def generate_food_position(self):
        while True:
            food_position = (
                randint(1, (Window.width - 40) // self.block_size) * self.block_size,
                randint(1, (Window.height - 40) // self.block_size) * self.block_size
            )
            if food_position not in self.snake:
                return food_position

    def update(self, dt):
        if not self.game_over:
            self.move_snake()
            self.check_collision()
            self.check_food_collision()
            self.draw()
        else:
            Clock.unschedule(self.update)
            self.show_game_over_popup()

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            # Snake
            Color(0, 1, 0)
            for segment in self.snake:
                Rectangle(pos=segment, size=(self.block_size, self.block_size))

            # Food
            Color(1, 0, 0)
            Rectangle(pos=self.food, size=(self.block_size, self.block_size))

            # Walls
            Color(0, 0, 1)
            # Top
            Rectangle(pos=(0, Window.height - self.wall_thickness),
                      size=(Window.width, self.wall_thickness))
            # Bottom
            Rectangle(pos=(0, 0),
                      size=(Window.width, self.wall_thickness))
            # Left
            Rectangle(pos=(0, 0),
                      size=(self.wall_thickness, Window.height))
            # Right
            Rectangle(pos=(Window.width - self.wall_thickness, 0),
                      size=(self.wall_thickness, Window.height))

    def show_game_over_popup(self):
        layout = BoxLayout(orientation='vertical', padding=10)
        label = Label(text=f"Game Over\nScore: {self.score}", font_size=24)
        restart_button = Button(text="Restart", size_hint=(1, 0.2))
        close_button = Button(text="Return to Menu", size_hint=(1, 0.2))

        layout.add_widget(label)
        layout.add_widget(restart_button)
        layout.add_widget(close_button)

        popup = Popup(title="Game Over", content=layout, size_hint=(0.6, 0.4))

        restart_button.bind(on_release=lambda *args: self.restart_game(popup))
        close_button.bind(on_release=lambda *args: self.close_game(popup))

        popup.open()

    def restart_game(self, popup):
        # Reset snake and state
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.snake_direction = 'RIGHT'
        self.food = self.generate_food_position()
        self.game_over = False
        self.score = 0
        self.score_label.text = f"Score: {self.score}"

        popup.dismiss()
        Clock.schedule_interval(self.update, SNAKE_FPS)

    def close_game(self, popup):
        # Stop game and return to menu
        Clock.unschedule(self.update)
        Window.unbind(on_key_down=self.on_key_down)
        app = App.get_running_app()
        app.root.clear_widgets()
        popup.dismiss()
        app.root.add_widget(LaunchMenu())

# ============================================================
#                        SOLITAIRE
# ============================================================

# Core game classes

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.is_face_up = False

    def flip(self):
        self.is_face_up = not self.is_face_up

    def is_red(self):
        return self.suit in ['H', 'D']

    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    suits = ['H', 'D', 'C', 'S']
    ranks = ['A', '2', '3', '4', '5', '6', '7',
             '8', '9', '10', 'J', 'Q', 'K']

    def __init__(self):
        self.cards = [Card(rank, suit)
                      for suit in self.suits
                      for rank in self.ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop() if self.cards else None

RANK_VALUES = {rank: i for i, rank in enumerate(Deck.ranks)}

class Solitaire:
    def __init__(self):
        self.deck = Deck()
        self.waste_pile = []
        self.tableau = [[] for _ in range(7)]
        self.foundation = [[] for _ in range(4)]
        self.deal_initial_tableau()

    def deal_initial_tableau(self):
        for i in range(7):
            for j in range(i, 7):
                card = self.deck.deal_card()
                if card:
                    self.tableau[j].append(card)
                    if j == i:
                        card.flip()

    def deal_from_deck(self):
        if self.deck.cards:
            card = self.deck.deal_card()
            if card:
                card.flip()
                self.waste_pile.append(card)
        elif self.waste_pile:
            self.deck.cards = list(reversed(self.waste_pile))
            for card in self.deck.cards:
                card.is_face_up = False
            self.waste_pile.clear()

    def rank_value(self, rank):
        return RANK_VALUES[rank]

    def can_stack(self, card1, card2):
        return (
            card1.is_red() != card2.is_red()
            and self.rank_value(card1.rank) + 1 == self.rank_value(card2.rank)
        )

    def can_move_to_foundation(self, card, pile):
        if not pile:
            return card.rank == 'A'
        top = pile[-1]
        return (
            top.suit == card.suit
            and self.rank_value(card.rank) == self.rank_value(top.rank) + 1
        )

    def check_win(self):
        return all(len(pile) == 13 for pile in self.foundation)

class CardWidget(Widget):
    def __init__(self, card, source, index, on_select, **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.source = source
        self.index = index
        self.on_select = on_select
        self.selected = False
        self.target_highlight = False

        self.size_hint = (None, None)
        self.size = (80, 120)

        self.bind(pos=self.draw_card)
        self.bind(size=self.draw_card)
        self.draw_card()

    def draw_card(self, *args):
        self.canvas.clear()
        self.clear_widgets()
        with self.canvas:
            if self.card.is_face_up:
                if self.card.is_red():
                    Color(1, 0.8, 0.8, 1)
                else:
                    Color(0.8, 0.9, 1, 1)
            else:
                Color(0.6, 0.6, 0.6, 1)
            Rectangle(pos=self.pos, size=self.size)

            if self.selected:
                Color(1, 1, 0, 1)
                Line(rectangle=(self.x - 2, self.y - 2,
                                self.width + 4, self.height + 4), width=2)

            if self.target_highlight:
                Color(0, 1, 0, 1)
                Line(rectangle=(self.x - 3, self.y - 3,
                                self.width + 6, self.height + 6), width=2)

            Color(0, 0, 0, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

        if self.card.is_face_up:
            label = Label(
                text=str(self.card),
                color=(1, 0, 0, 1) if self.card.is_red() else (0, 0, 0, 1),
                size_hint=(None, None),
                size=(40, 30),
                pos=(self.x + 5, self.top - 35),
                halign='left',
                valign='top'
            )
            label.bind(size=label.setter('text_size'))
            self.add_widget(label)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.card.is_face_up:
            self.on_select(self)
            return True
        return super().on_touch_down(touch)

class Placeholder(Widget):
    def __init__(self, source, index, label_text, on_empty_touch, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.index = index
        self.card = None
        self.on_empty_touch = on_empty_touch
        self.label_text = label_text
        self.size_hint = (None, None)
        self.size = (80, 120)

        self.bind(pos=self.draw_placeholder)
        self.bind(size=self.draw_placeholder)
        self.draw_placeholder()

    def draw_placeholder(self, *args):
        self.canvas.clear()
        self.clear_widgets()
        with self.canvas:
            Color(0.5, 0.5, 0.5, 0.3)
            Rectangle(pos=self.pos, size=self.size)
            Color(0.2, 0.2, 0.2, 0.5)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

        label = Label(
            text=self.label_text,
            font_size=24,
            color=(0.2, 0.2, 0.2, 0.5),
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
            halign='center',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        self.add_widget(label)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return self.on_empty_touch(self, touch)
        return super().on_touch_down(touch)

class SolitaireWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_game()

    def start_game(self, *args):
        self.clear_widgets()
        self.game = Solitaire()
        self.selected = None
        self.card_widgets = []
        self.draw_board()

    def draw_board(self):
        self.clear_widgets()
        self.card_widgets.clear()

        # Buttons
        deck_btn = Button(
            text='Draw',
            size_hint=(None, None),
            size=(80, 40),
            pos=(20, Window.height - 80)
        )
        deck_btn.bind(on_press=self.draw_card)
        self.add_widget(deck_btn)

        restart_btn = Button(
            text='Restart',
            size_hint=(None, None),
            size=(100, 40),
            pos=(120, Window.height - 80)
        )
        restart_btn.bind(on_press=self.start_game)
        self.add_widget(restart_btn)

        menu_btn = Button(
            text='Menu',
            size_hint=(None, None),
            size=(80, 40),
            pos=(240, Window.height - 80)
        )
        menu_btn.bind(on_press=self.return_to_menu)
        self.add_widget(menu_btn)

        # Waste pile
        if self.game.waste_pile:
            card = self.game.waste_pile[-1]
            cw = CardWidget(card, source='waste', index=0,
                            on_select=self.select_card)
            cw.pos = (240, Window.height - 120)
            self.card_widgets.append(cw)
            self.add_widget(cw)

        # Foundations
        for i, pile in enumerate(self.game.foundation):
            x = 400 + i * 100
            y = Window.height - 120
            if pile:
                card = pile[-1]
                cw = CardWidget(card, source='foundation', index=i,
                                on_select=self.select_card)
                cw.pos = (x, y)
                self.card_widgets.append(cw)
                self.add_widget(cw)
            else:
                placeholder = Placeholder(
                    source='foundation',
                    index=i,
                    label_text='A',
                    on_empty_touch=self.handle_empty_foundation_touch,
                    pos=(x, y)
                )
                self.add_widget(placeholder)

        # Tableau
        for i, pile in enumerate(self.game.tableau):
            x = 20 + i * 120
            if pile:
                for j, card in enumerate(pile):
                    cw = CardWidget(card, source='tableau', index=i,
                                    on_select=self.select_card)
                    cw.pos = (x, Window.height - 250 - j * 30)
                    self.card_widgets.append(cw)
                    self.add_widget(cw)
            else:
                placeholder = Placeholder(
                    source='tableau',
                    index=i,
                    label_text='K',
                    on_empty_touch=self.handle_empty_tableau_touch,
                    pos=(x, Window.height - 250)
                )
                self.add_widget(placeholder)

        if self.game.check_win():
            win_label = Label(
                text='You Win!',
                font_size=40,
                size_hint=(None, None),
                size=(200, 100),
                pos=(400, 300),
                color=(0, 1, 0, 1)
            )
            self.add_widget(win_label)

    def draw_card(self, *args):
        self.game.deal_from_deck()
        self.clear_selection_and_targets()
        self.draw_board()

    def clear_selection_and_targets(self):
        if self.selected:
            self.selected.selected = False
            self.selected.draw_card()
            self.selected = None
        for cw in self.card_widgets:
            cw.target_highlight = False
            cw.draw_card()

    def select_card(self, widget):
        if self.selected is None:
            self.selected = widget
            widget.selected = True
            widget.draw_card()
            self.highlight_valid_targets()
            return

        if self.selected == widget:
            self.clear_selection_and_targets()
            return

        if self.try_move_to_foundation(widget):
            self.after_successful_move()
            return

        if self.try_move_within_tableau(widget):
            self.after_successful_move()
            return

        if self.try_waste_to_tableau(widget):
            self.after_successful_move()
            return

        self.clear_selection_and_targets()

    def after_successful_move(self):
        self.clear_selection_and_targets()
        self.draw_board()

    def cancel_selection(self):
        self.clear_selection_and_targets()

    def try_move_to_foundation(self, target_widget):
        if self.selected is None:
            return False

        card = self.selected.card
        for i in range(4):
            pile = self.game.foundation[i]
            if self.game.can_move_to_foundation(card, pile):
                self._remove_card_from_source(self.selected)
                pile.append(card)
                return True
        return False

    def try_move_within_tableau(self, target_widget):
        if self.selected is None:
            return False
        if target_widget.source != 'tableau':
            return False

        from_index = self.selected.index
        to_index = target_widget.index
        from_pile = self.game.tableau[from_index]
        to_pile = self.game.tableau[to_index]
        card = self.selected.card

        try:
            card_idx = from_pile.index(card)
        except ValueError:
            return False

        moving_stack = from_pile[card_idx:]

        if not moving_stack:
            return False

        first_card = moving_stack[0]

        if not to_pile:
            # Only Kings can go to empty tableau piles
            if first_card.rank != 'K':
                return False
            self.game.tableau[from_index] = from_pile[:card_idx]
            to_pile.extend(moving_stack)
        else:
            # Check if we can stack on top of the last card in to_pile
            if not self.game.can_stack(first_card, to_pile[-1]):
                return False
            self.game.tableau[from_index] = from_pile[:card_idx]
            to_pile.extend(moving_stack)

        # Flip new top if necessary
        if self.game.tableau[from_index]:
            top_card = self.game.tableau[from_index][-1]
            if not top_card.is_face_up:
                top_card.flip()

        return True

    def try_waste_to_tableau(self, target_widget):
        if self.selected is None:
            return False
        if self.selected.source != 'waste':
            return False
        if target_widget.source != 'tableau':
            return False

        card = self.selected.card
        to_pile = self.game.tableau[target_widget.index]

        if (not to_pile and card.rank == 'K') or \
           (to_pile and self.game.can_stack(card, to_pile[-1])):
            self.game.waste_pile.pop()
            to_pile.append(card)
            return True

        return False

    def _remove_card_from_source(self, widget):
        if widget.source == 'waste':
            if self.game.waste_pile:
                self.game.waste_pile.pop()
        elif widget.source == 'tableau':
            pile = self.game.tableau[widget.index]
            if widget.card in pile:
                pile.remove(widget.card)
                if pile and not pile[-1].is_face_up:
                    pile[-1].flip()
        elif widget.source == 'foundation':
            pile = self.game.foundation[widget.index]
            if pile:
                pile.pop()

    def handle_empty_tableau_touch(self, placeholder, touch):
        if not (self.selected and placeholder.collide_point(*touch.pos)):
            return False
        card = self.selected.card
        if card.rank != 'K':
            self.cancel_selection()
            return False

        to_pile = self.game.tableau[placeholder.index]
        self._remove_card_from_source(self.selected)
        to_pile.append(card)
        self.after_successful_move()
        return True

    def handle_empty_foundation_touch(self, placeholder, touch):
        if not (self.selected and placeholder.collide_point(*touch.pos)):
            return False
        card = self.selected.card
        if card.rank != 'A':
            self.cancel_selection()
            return False

        to_pile = self.game.foundation[placeholder.index]
        self._remove_card_from_source(self.selected)
        to_pile.append(card)
        self.after_successful_move()
        return True

    def highlight_valid_targets(self):
        if self.selected is None:
            return

        my_card = self.selected.card

        for cw in self.card_widgets:
            cw.target_highlight = False
            cw.draw_card()

        # Foundation targets
        for i, pile in enumerate(self.game.foundation):
            if self.game.can_move_to_foundation(my_card, pile):
                for cw in self.card_widgets:
                    if cw.source == 'foundation' and cw.index == i:
                        cw.target_highlight = True
                        cw.draw_card()

        # Tableau targets (non-empty piles)
        for i, pile in enumerate(self.game.tableau):
            if not pile:
                continue
            top = pile[-1]
            if self.game.can_stack(my_card, top):
                for cw in self.card_widgets:
                    if cw.source == 'tableau' and cw.index == i and cw.card is top:
                        cw.target_highlight = True
                        cw.draw_card()

    def return_to_menu(self, *args):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(LaunchMenu())

# ============================================================
#                        ASTEROIDS
# ============================================================

class Settings:
    ASTEROID_MIN_SPEED = 2.0
    ASTEROID_MAX_SPEED = 2.0
    ASTEROID_MIN_SIZE = 25
    ASTEROID_MAX_SIZE = 40

    BULLET_SPEED = 15
    BULLET_SIZE_X = 10
    BULLET_SIZE_Y = 10

    SPACESHIP_SIZE = 40
    INITIAL_LIVES = 3

    BULLET_COOLDOWN = 0.2
    MIN_BULLET_COOLDOWN = 0.05

    INVINCIBILITY_DURATION = 2.0
    ASTEROID_SPAWN_INTERVAL = 1.2
    MIN_SPAWN_INTERVAL = 0.4
    SCORE_INCREMENT = 10

    EXP_PER_ASTEROID = 10
    START_EXP_TO_NEXT_LEVEL = 50

    CONTINUUM_DURATION = 5.0
    BIG_BULLET_DURATION = 5.0

KEY_UP = 'up'
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_SHOOT = 'spacebar'
KEY_PAUSE = 'p'
KEY_RESTART = 'r'
KEY_MUTE = 'm'

KEYCODE_TO_ACTION = {
    273: KEY_UP,
    274: None,
    275: KEY_RIGHT,
    276: KEY_LEFT,
    32: KEY_SHOOT,
    112: KEY_PAUSE,
    114: KEY_RESTART,
    109: KEY_MUTE,
}

shoot_sound = SoundLoader.load('shoot.wav')
explosion_sound = SoundLoader.load('explosion.wav')
background_music = SoundLoader.load('background_music.mp3')
sound_enabled = True

def play_sound(sound):
    global sound_enabled
    if sound_enabled and sound:
        sound.play()

class GameState(Enum):
    START_SCREEN = auto()
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()

class Spaceship(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(0, 0)
        self.angle = 0
        self.thrust = 50
        self.turn_speed = 5
        self.drag = 0.78
        self.last_shot_time = 0.0
        self.invincible = False
        self.invincibility_timer = 0.0
        self.is_stone = False
        self.stone_duration = 0.0
        self.collision_radius = Settings.SPACESHIP_SIZE * 0.6

        self.key_states = {
            KEY_UP: False,
            KEY_LEFT: False,
            KEY_RIGHT: False
        }

        with self.canvas:
            self.color = Color(0, 0, 1)
            self.shape = Line(width=2)

        self.update_shape()

    def update_shape(self):
        half = Settings.SPACESHIP_SIZE / 2.0
        points = [
            Vector(-half, -half),
            Vector(0, half),
            Vector(half, -half),
            Vector(-half, -half)
        ]
        rotated_points = [Vector(*p).rotate(self.angle) + self.center for p in points]
        self.shape.points = [coord for point in rotated_points for coord in point]

    def move(self, dt):
        if self.is_stone:
            self.pos = Vector(*self.pos) + self.velocity * dt
            self.wrap_around_screen()
            self.stone_duration -= dt
            if self.stone_duration <= 0:
                self.stop_stone()
            self.update_shape()
            return

        if self.key_states.get(KEY_UP, False):
            self.accelerate()
        if self.key_states.get(KEY_LEFT, False):
            self.rotate(1)
        if self.key_states.get(KEY_RIGHT, False):
            self.rotate(-1)

        self.velocity *= self.drag
        self.pos = Vector(*self.pos) + self.velocity * dt
        self.wrap_around_screen()
        self.update_shape()

    def stop_stone(self):
        self.is_stone = False
        self.color.rgb = (0, 0, 1)

    def wrap_around_screen(self):
        if self.x > Window.width:
            self.x = 0
        if self.right < 0:
            self.x = Window.width
        if self.y > Window.height:
            self.y = 0
        if self.top < 0:
            self.y = Window.height

    def rotate(self, direction):
        self.angle += self.turn_speed * direction
        self.angle %= 360

    def accelerate(self):
        force = Vector(0, self.thrust).rotate(self.angle)
        self.velocity += force

    def set_invincible(self, duration):
        self.invincible = True
        self.invincibility_timer = duration
        Clock.unschedule(self.flash_effect)
        Clock.schedule_interval(self.flash_effect, 0.1)

    def flash_effect(self, dt):
        if self.is_stone:
            return

        if self.invincibility_timer > 0:
            if self.color.rgb == (1, 0, 1):
                self.color.rgb = (1, 0, 0)
            else:
                self.color.rgb = (1, 0, 1)
            self.invincibility_timer -= dt
        else:
            self.invincible = False
            self.color.rgb = (0, 0, 1)
            Clock.unschedule(self.flash_effect)

    def apply_stone(self, duration):
        self.is_stone = True       
        self.invincible = True
        self.stone_duration = duration
        self.color.rgb = (0.5, 0.5, 0.5)

class Asteroid(Widget):
    def __init__(self, size_level=3, **kwargs):
        super().__init__(**kwargs)
        self.size_level = size_level

        if self.size_level == 3:
            base_size = Settings.ASTEROID_MAX_SIZE
        elif self.size_level == 2:
            base_size = (Settings.ASTEROID_MIN_SIZE + Settings.ASTEROID_MAX_SIZE) / 2
        else:
            base_size = Settings.ASTEROID_MIN_SIZE

        self.size = (base_size, base_size)
        self.collision_radius = self.width / 2.0

        self.speed = uniform(Settings.ASTEROID_MIN_SPEED,
                             Settings.ASTEROID_MAX_SPEED)
        self.angle = uniform(0, 360)
        self.velocity = Vector(0, self.speed).rotate(self.angle)
        self.pos = (
            randint(0, max(0, int(Window.width - self.width))),
            randint(0, max(0, int(Window.height - self.height)))
        )
        with self.canvas:
            Color(0.5, 0.5, 0.5)
            self.shape = Ellipse(size=self.size, pos=self.pos)

    def move(self):
        self.pos = Vector(*self.pos) + self.velocity
        self.shape.pos = self.pos
        self.wrap_around_screen()

    def wrap_around_screen(self):
        if self.x > Window.width:
            self.x = 0
        if self.right < 0:
            self.x = Window.width
        if self.y > Window.height:
            self.y = 0
        if self.top < 0:
            self.y = Window.height

class HostileAsteroid(Asteroid):
    def __init__(self, target, size_level=3, **kwargs):
        super().__init__(size_level=size_level, **kwargs)
        self.target = target
        with self.canvas:
            Color(0.7, 0.7, 0.7)

    def move(self):
        target_position = Vector(self.target.center_x, self.target.center_y)
        direction = (target_position - Vector(*self.pos))
        if direction.length() != 0:
            direction = direction.normalize()
        self.velocity = direction * self.speed
        super().move()

class Bullet(Widget):
    def __init__(self, spaceship, continuum=False, big_bullet=False, **kwargs):
        super().__init__(**kwargs)
        self.size = (Settings.BULLET_SIZE_X, Settings.BULLET_SIZE_Y)
        self.continuum = continuum
        self.big_bullet = big_bullet

        tip_position = Vector(0, spaceship.height / 2).rotate(spaceship.angle) + spaceship.center
        self.pos = tip_position - Vector(self.width / 2, self.height / 2)
        self.velocity = Vector(0, Settings.BULLET_SPEED).rotate(spaceship.angle)

        with self.canvas:
            Color(1, 0, 0)
            self.shape = Ellipse(size=self.size, pos=self.pos)

        self.collision_radius = self.width / 2.0

        if self.big_bullet:
            self.apply_big_bullet()

    def move(self):
        self.pos = Vector(*self.pos) + self.velocity
        self.shape.pos = self.pos

        if self.continuum:
            self.wrap_around_screen()
        else:
            if not (0 <= self.x <= Window.width and 0 <= self.y <= Window.height):
                if self.parent:
                    self.parent.remove_widget(self)

    def wrap_around_screen(self):
        if self.x > Window.width:
            self.x = 0
        if self.right < 0:
            self.x = Window.width
        if self.y > Window.height:
            self.y = 0
        if self.top < 0:
            self.y = Window.height

    def apply_big_bullet(self):
        self.big_bullet = True
        self.size = (self.size[0] * 1.2, self.size[1] * 1.2)
        self.shape.size = self.size
        self.shape.pos = self.pos
        self.collision_radius = self.width / 2.0

class Pickup(Widget):
    def __init__(self, effect, **kwargs):
        super().__init__(**kwargs)
        self.effect = effect
        self.size = (30, 30)
        self.pos = (
            randint(0, max(0, int(Window.width - self.width))),
            randint(0, max(0, int(Window.height - self.height)))
        )
        with self.canvas:
            if self.effect == "health":
                Color(0, 1, 0)
            elif self.effect == "shield":
                Color(0, 0, 1)
            elif self.effect == "score_multiplier":
                Color(1, 1, 0)
            elif self.effect == "fire_rate":
                Color(1, 0, 1)
            elif self.effect == "stone":
                Color(1, 1, 1)
            elif self.effect == "continuum":
                Color(0.5, 0.5, 0.8)
            elif self.effect == "big_bullet":
                Color(1, 0, 0)
            elif self.effect == "bomb":
                Color(0.1, 0.1, 0.1)
            self.shape = Ellipse(size=self.size, pos=self.pos)

        self.collision_radius = self.width / 2.0

    def apply_effect(self, game):
        if self.effect == "health" and game.lives < 5:
            game.lives += 1
            game.lives_label.text = f"Lives: {game.lives}"

        elif self.effect == "shield":
            game.spaceship.set_invincible(5.0)

        elif self.effect == "score_multiplier":
            game.score += 100
            game.score_label.text = f"Score: {game.score}"

        elif self.effect == "fire_rate":
            game.apply_fire_rate_effect()

        elif self.effect == "stone":
            game.spaceship.apply_stone(5.0)
            game.spaceship.set_invincible(5.0)

        elif self.effect == "continuum":
            game.enable_continuum(Settings.CONTINUUM_DURATION)

        elif self.effect == "big_bullet":
            game.enable_big_bullet(Settings.BIG_BULLET_DURATION)

        elif self.effect == "bomb":
            for asteroid in game.asteroids[:]:
                game.remove_widget(asteroid)
                game.asteroids.remove(asteroid)
            self.show_bomb_explosion(game)

    def show_bomb_explosion(self, game):
        with game.canvas:
            Color(1, 0.5, 0, 0.7)
            explosion = Ellipse(size=(200, 200),
                                pos=(self.center_x - 100, self.center_y - 100))

        def remove_explosion(dt):
            game.canvas.remove(explosion)

        Clock.schedule_once(remove_explosion, 0.5)

class AsteroidGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Background
        with self.canvas.before:
            Color(0, 0, 0)
            self.bg = Rectangle(size=Window.size, pos=(0, 0))

        # Core state
        self.spaceship = Spaceship(center=(Window.width / 2, Window.height / 2))
        self.add_widget(self.spaceship)

        self.bullets = []
        self.asteroids = []
        self.pickups = []

        self.score = 0
        self.lives = Settings.INITIAL_LIVES
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = Settings.START_EXP_TO_NEXT_LEVEL

        self.state = GameState.START_SCREEN

        self.asteroid_spawn_rate = Settings.ASTEROID_SPAWN_INTERVAL
        self.current_bullet_cooldown = Settings.BULLET_COOLDOWN

        self.continuum_active_until = 0.0
        self.big_bullet_active_until = 0.0

        # HUD
        self.score_label = Label(
            text=f"Score: {self.score}",
            pos=(10, Window.height - 40),
            size_hint=(None, None)
        )
        self.lives_label = Label(
            text=f"Lives: {self.lives}",
            pos=(10, Window.height - 70),
            size_hint=(None, None)
        )
        self.level_label = Label(
            text=f"Level: {self.level}",
            pos=(10, Window.height - 100),
            size_hint=(None, None)
        )

        self.start_label = Label(
            text="ASTEROIDS\n\nPress SPACE to start\nArrows: Move  |  P: Pause  |  R: Restart\nM: Mute sound",
            font_size=24,
            halign='center',
            valign='middle',
            size_hint=(None, None),
            pos=(Window.width / 2 - 200, Window.height / 2 - 50)
        )

        self.add_widget(self.score_label)
        self.add_widget(self.lives_label)
        self.add_widget(self.level_label)
        self.add_widget(self.start_label)

        # Menu button
        self.menu_button = Button(
            text="Return to Menu",
            size_hint=(0.2, 0.1),
            pos_hint={'x': 0, 'y': 0.9}
        )
        self.menu_button.bind(on_release=lambda *args: self.return_to_menu())
        self.add_widget(self.menu_button)

        # Schedules
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Clock.schedule_interval(self.spawn_asteroid, self.asteroid_spawn_rate)
        Clock.schedule_interval(self.spawn_pickup, 6.0)

        # Bind keys
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

        # Background music
        if background_music and sound_enabled:
            background_music.loop = True
            background_music.play()

    def toggle_pause(self):
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING

    def start_game(self):
        if self.state == GameState.START_SCREEN:
            self.state = GameState.RUNNING
            if self.start_label in self.children:
                self.remove_widget(self.start_label)

    def game_over(self):
        if self.state == GameState.GAME_OVER:
            return
        self.state = GameState.GAME_OVER
        if not hasattr(self, 'game_over_label'):
            self.game_over_label = Label(
                text="Game Over!\nPress 'R' to Restart",
                font_size=40,
                halign='center',
                valign='middle',
                size_hint=(None, None),
                pos=(Window.width / 2 - 200, Window.height / 2)
            )
            self.add_widget(self.game_over_label)

    def spawn_pickup(self, dt):
        if self.state != GameState.RUNNING:
            return
        effects = [
            "health", "shield", "score_multiplier", "fire_rate",
            "stone", "continuum", "big_bullet", "bomb"
        ]
        effect = effects[randint(0, len(effects) - 1)]
        pickup = Pickup(effect)
        self.add_widget(pickup)
        self.pickups.append(pickup)

    def spawn_asteroid(self, dt):
        if self.state != GameState.RUNNING:
            return
        asteroid_type = HostileAsteroid if randint(0, 8) == 0 else Asteroid

        if asteroid_type == HostileAsteroid:
            asteroid = HostileAsteroid(target=self.spaceship, size_level=3)
        else:
            asteroid = Asteroid(size_level=3)

        if not any(self.check_collision(asteroid, obj) for obj in self.asteroids + [self.spaceship]):
            self.add_widget(asteroid)
            self.asteroids.append(asteroid)
        else:
            asteroid.canvas.clear()

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.lives += 1
        self.exp_to_next_level += 50

        Settings.ASTEROID_MIN_SPEED *= 1.05
        Settings.ASTEROID_MAX_SPEED *= 1.05

        self.asteroid_spawn_rate = max(
            Settings.MIN_SPAWN_INTERVAL,
            self.asteroid_spawn_rate * 0.9
        )

        self.apply_fire_rate_effect()

        Clock.unschedule(self.spawn_asteroid)
        Clock.schedule_interval(self.spawn_asteroid, self.asteroid_spawn_rate)

        self.level_label.text = f"Level: {self.level}"

    def apply_fire_rate_effect(self):
        cooldown_reduction = 0.9
        self.current_bullet_cooldown = max(
            Settings.MIN_BULLET_COOLDOWN,
            self.current_bullet_cooldown * cooldown_reduction
        )

    def enable_continuum(self, duration):
        self.continuum_active_until = Clock.get_time() + duration

    def enable_big_bullet(self, duration):
        self.big_bullet_active_until = Clock.get_time() + duration

    def bullet_continuum_active(self):
        return Clock.get_time() < self.continuum_active_until

    def bullet_big_bullet_active(self):
        return Clock.get_time() < self.big_bullet_active_until

    def shoot_bullet(self):
        if self.state == GameState.START_SCREEN:
            self.start_game()
            return

        if self.state != GameState.RUNNING:
            return

        now = Clock.get_time()
        if now - self.spaceship.last_shot_time >= self.current_bullet_cooldown:
            play_sound(shoot_sound)
            bullet = Bullet(
                self.spaceship,
                continuum=self.bullet_continuum_active(),
                big_bullet=self.bullet_big_bullet_active()
            )
            self.add_widget(bullet)
            self.bullets.append(bullet)
            self.spaceship.last_shot_time = now

    def update(self, dt):
        if self.state != GameState.RUNNING:
            return

        self.spaceship.move(dt)

        for bullet in self.bullets[:]:
            bullet.move()
            if (not bullet.continuum and
                    not (0 <= bullet.x <= Window.width and 0 <= bullet.y <= Window.height)):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

        for asteroid in self.asteroids[:]:
            asteroid.move()
            if self.check_collision(self.spaceship, asteroid):
                self.handle_collision(asteroid)

        for pickup in self.pickups[:]:
            if self.check_collision(self.spaceship, pickup):
                pickup.apply_effect(self)
                if pickup in self.pickups:
                    self.pickups.remove(pickup)
                self.remove_widget(pickup)

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if self.check_collision(bullet, asteroid):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if bullet.parent:
                        self.remove_widget(bullet)
                    self.destroy_asteroid(asteroid)
                    break

    def destroy_asteroid(self, asteroid):
        if asteroid in self.asteroids:
            self.asteroids.remove(asteroid)
        self.remove_widget(asteroid)
        play_sound(explosion_sound)

        self.score += Settings.SCORE_INCREMENT
        self.score_label.text = f"Score: {self.score}"
        self.gain_exp(Settings.EXP_PER_ASTEROID)

        if asteroid.size_level > 1:
            new_level = asteroid.size_level - 1
            for _ in range(2):
                if isinstance(asteroid, HostileAsteroid):
                    new_ast = HostileAsteroid(
                        target=self.spaceship,
                        size_level=new_level
                    )
                else:
                    new_ast = Asteroid(size_level=new_level)

                new_ast.pos = asteroid.pos[:]
                if not any(self.check_collision(new_ast, obj)
                           for obj in self.asteroids + [self.spaceship]):
                    self.add_widget(new_ast)
                    self.asteroids.append(new_ast)
                else:
                    new_ast.canvas.clear()

    def handle_collision(self, asteroid):
        if self.spaceship.is_stone:
            if asteroid in self.asteroids:
                self.asteroids.remove(asteroid)
            self.remove_widget(asteroid)
            self.spaceship.set_invincible(5.0)
            self.score += Settings.SCORE_INCREMENT
            self.score_label.text = f"Score: {self.score}"
            play_sound(explosion_sound)
            return

        if not self.spaceship.invincible:
            self.lives -= 1
            self.lives_label.text = f"Lives: {self.lives}"
            self.spaceship.set_invincible(Settings.INVINCIBILITY_DURATION)

            if asteroid in self.asteroids:
                self.asteroids.remove(asteroid)
            self.remove_widget(asteroid)
            play_sound(explosion_sound)

            if self.lives <= 0:
                self.game_over()

    def check_collision(self, obj1, obj2):
        obj1_center = Vector(obj1.center_x, obj1.center_y)
        obj2_center = Vector(obj2.center_x, obj2.center_y)
        distance = obj1_center.distance(obj2_center)

        obj1_radius = getattr(obj1, 'collision_radius', obj1.width / 2.0)
        obj2_radius = getattr(obj2, 'collision_radius', obj2.width / 2.0)

        return distance < (obj1_radius + obj2_radius)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        global sound_enabled

        action = KEYCODE_TO_ACTION.get(key, None)
        if action is None:
            return

        if action == KEY_PAUSE:
            if self.state in (GameState.RUNNING, GameState.PAUSED):
                self.toggle_pause()

        elif action == KEY_SHOOT:
            self.shoot_bullet()

        elif action == KEY_UP:
            self.spaceship.key_states[KEY_UP] = True

        elif action == KEY_LEFT:
            self.spaceship.key_states[KEY_LEFT] = True

        elif action == KEY_RIGHT:
            self.spaceship.key_states[KEY_RIGHT] = True

        elif action == KEY_RESTART:
            if self.state in (GameState.GAME_OVER, GameState.PAUSED):
                self.restart_game()

        elif action == KEY_MUTE:
            sound_enabled = not sound_enabled
            if background_music:
                if sound_enabled:
                    background_music.loop = True
                    background_music.play()
                else:
                   
                                        background_music.stop()

    def on_key_up(self, window, key, scancode):
        action = KEYCODE_TO_ACTION.get(key, None)
        if action is None:
            return

        if action == KEY_UP:
            self.spaceship.key_states[KEY_UP] = False
        elif action == KEY_LEFT:
            self.spaceship.key_states[KEY_LEFT] = False
        elif action == KEY_RIGHT:
            self.spaceship.key_states[KEY_RIGHT] = False

    def restart_game(self):
        if hasattr(self, 'game_over_label'):
            self.remove_widget(self.game_over_label)
            del self.game_over_label

        for bullet in self.bullets[:]:
            self.remove_widget(bullet)
        for asteroid in self.asteroids[:]:
            self.remove_widget(asteroid)
        for pickup in self.pickups[:]:
            self.remove_widget(pickup)

        self.bullets.clear()
        self.asteroids.clear()
        self.pickups.clear()

        self.score = 0
        self.lives = Settings.INITIAL_LIVES
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = Settings.START_EXP_TO_NEXT_LEVEL
        self.state = GameState.RUNNING

        self.asteroid_spawn_rate = Settings.ASTEROID_SPAWN_INTERVAL
        self.current_bullet_cooldown = Settings.BULLET_COOLDOWN

        self.continuum_active_until = 0.0
        self.big_bullet_active_until = 0.0

        self.score_label.text = f"Score: {self.score}"
        self.lives_label.text = f"Lives: {self.lives}"
        self.level_label.text = f"Level: {self.level}"

        self.spaceship.center = (Window.width / 2, Window.height / 2)
        self.spaceship.velocity = Vector(0, 0)
        self.spaceship.angle = 0
        self.spaceship.is_stone = False
        self.spaceship.invincible = False
        self.spaceship.color.rgb = (0, 0, 1)
        self.spaceship.update_shape()

        Clock.unschedule(self.spawn_asteroid)
        Clock.schedule_interval(self.spawn_asteroid, self.asteroid_spawn_rate)

    def return_to_menu(self):
        Clock.unschedule(self.update)
        Clock.unschedule(self.spawn_asteroid)
        Clock.unschedule(self.spawn_pickup)
        Window.unbind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        if background_music:
            background_music.stop()
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(LaunchMenu())


# ============================================================
#                        LAUNCHER
# ============================================================

class LaunchMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20

        self.add_widget(Label(text="Game Menu",
                              font_size=32,
                              size_hint=(1, 0.15)))
        self.add_widget(Label(text="Select AI Difficulty (for Pong)",
                              size_hint=(1, 0.1)))

        self.difficulty_slider = Slider(
            min=1, max=10, value=5, step=1, size_hint=(1, 0.1)
        )
        self.add_widget(self.difficulty_slider)

        start_pong_button = Button(text="Start Pong Game",
                                   size_hint=(1, 0.12))
        start_pong_button.bind(on_release=self.start_pong_game)
        self.add_widget(start_pong_button)

        start_brick_button = Button(text="Start Brick Break Game",
                                    size_hint=(1, 0.12))
        start_brick_button.bind(on_release=self.start_brick_game)
        self.add_widget(start_brick_button)

        start_snake_button = Button(text="Start Snake Game",
                                    size_hint=(1, 0.12))
        start_snake_button.bind(on_release=self.start_snake_game)
        self.add_widget(start_snake_button)

        start_solitaire_button = Button(text="Start Solitaire",
                                        size_hint=(1, 0.12))
        start_solitaire_button.bind(on_release=self.start_solitaire)
        self.add_widget(start_solitaire_button)

        start_asteroid_button = Button(text="Start Asteroids",
                                       size_hint=(1, 0.12))
        start_asteroid_button.bind(on_release=self.start_asteroid)
        self.add_widget(start_asteroid_button)

    def start_pong_game(self, instance):
        self.clear_widgets()
        pong_game = PongGame(ai_difficulty=self.difficulty_slider.value)
        self.add_widget(pong_game)

    def start_brick_game(self, instance):
        self.clear_widgets()
        brick_game = BrickBreakGame()
        self.add_widget(brick_game)

    def start_snake_game(self, instance):
        self.clear_widgets()
        snake_game = SnakeGame()
        self.add_widget(snake_game)

    def start_solitaire(self, instance):
        self.clear_widgets()
        solitaire_game = SolitaireWidget()
        self.add_widget(solitaire_game)

    def start_asteroid(self, instance):
        self.clear_widgets()
        asteroid_game = AsteroidGame()
        self.add_widget(asteroid_game)


class ArcadeApp(App):
    def build(self):
        return LaunchMenu()


if __name__ == '__main__':
    ArcadeApp().run()


