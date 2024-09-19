from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import platform
from random import randint 
from kivy.uix.gridlayout import GridLayout

#Pong game starts here



class PongGame(Widget):

    def return_to_menu(self, instance):
        """Return to the main menu when the button is clicked."""
        Clock.unschedule(self.update)  # Stop the game loop
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(LaunchMenu())

    def __init__(self, ai_difficulty=5, paddle_color=(1, 1, 1), ball_color=(1, 1, 1), high_score=0, **kwargs):
        super().__init__(**kwargs)
        self.ai_difficulty = ai_difficulty
        self.ball_speed_multiplier = 1.1  # Ball speed multiplier on paddle hit
        self.ball_color = ball_color
        self.paddle_color = paddle_color
        self.ball_x = Window.width / 2
        self.ball_y = Window.height / 2
        self.ball_dx = (randint(1, 5) or 1) * self.ball_speed_multiplier
        self.ball_dy = (randint(1, 5) or 1) * self.ball_speed_multiplier
        self.paddle_width = 100
        self.paddle_height = 20
        self.player_score = 0
        self.ai_score = 0
        self.high_score = high_score
        self.win_score = 10  # Score to win
        self.player_y = Window.width / 2 - self.paddle_width / 2  # Player's paddle at the bottom
        self.ai_y = Window.height / 2 - self.paddle_height / 2  # AI's paddle at the top


        # Return to Menu Button
        self.menu_button = Button(text="Return to Menu", size_hint=(0.2, 0.1), pos_hint={'x': 0, 'y': 0.9})
        self.menu_button.bind(on_release=self.return_to_menu)
        self.add_widget(self.menu_button)

        # Score labels
        self.score_label1 = Label(text=f"Player: {self.player_score}", font_size=24,
                                  pos=(Window.width * 0.1, Window.height - 60))
        self.score_label2 = Label(text=f"AI: {self.ai_score}", font_size=24,
                                  pos=(Window.width * 0.7, Window.height - 60))
        self.add_widget(self.score_label1)
        self.add_widget(self.score_label2)

        # High score label
        self.high_score_label = Label(text=f"High Score: {self.high_score}", font_size=24,
                                      pos=(Window.width * 0.4, Window.height - 60))
        self.add_widget(self.high_score_label)

        with self.canvas:
            Color(*self.ball_color)
            self.ball = Ellipse(pos=(self.ball_x, self.ball_y), size=(20, 20))

            Color(*self.paddle_color)
            self.player = Rectangle(pos=(self.player_y, 20), size=(self.paddle_width, self.paddle_height))
            self.ai = Rectangle(pos=(self.ai_y, Window.height - self.paddle_height - 20), size=(self.paddle_width, self.paddle_height))

            Color(1, 1, 1, 1)  # Horizontal center line
            self.center_line = Line(points=[0, Window.height / 2, Window.width, Window.height / 2], width=2)

        # Schedule the update function to run every frame
        Clock.schedule_interval(self.update, 1.0 / 30.0)

        # Bind keyboard events
        self.bind(on_key_down=self.on_key_down)
        self.bind(on_touch_move=self.on_touch_move)

        # Movement variables
        self.move_left = False
        self.move_right = False

    def reset_ball(self):
        self.ball_x = Window.width / 2
        self.ball_y = Window.height / 2
        self.ball_dx = (randint(1, 5) or 1) * self.ball_speed_multiplier
        self.ball_dy = (randint(1, 5) or 1) * self.ball_speed_multiplier
        self.ball.pos = (self.ball_x, self.ball_y)

    def on_touch_move(self, touch, *args):
        if self.collide_point(touch.x, touch.y):  # Ensure the touch is within the widget bounds
         # Calculate new x position, ensuring the paddle stays within screen bounds
            self.player_y = min(max(touch.x - self.paddle_width / 2, 0), Window.width - self.paddle_width)
         # Update the player's position with the new x value, keeping y fixed
            self.player.pos = (self.player_y, self.player.pos[1])


    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        

        if keycode == 80:  # Left arrow key code (typically)
            self.move_left = True
        elif keycode == 79:  # Right arrow key code (typically)
            self.move_right = True


    def update(self, dt):
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        """Game update loop."""
        # Player movement
        if self.move_left:
            self.player_y = max(self.player_y - 5, 0)  # Move left and stay within boundaries
        if self.move_right:
            self.player_y = min(self.player_y + 5, Window.width - self.paddle_width)  # Move right within boundaries
        
            self.player.pos = (self.player_y, 20)

        

        # Ball collision with the vertical walls
        if self.ball_x <= 0 or self.ball_x >= Window.width - 20:
            self.ball_dx *= -1

        # Ball collision with paddles
        # Player's paddle
        if self.ball_y <= self.paddle_height + 20 and self.player_y <= self.ball_x + 20 <= self.player_y + self.paddle_width:
            self.ball_dy *= -1
            self.accelerate_ball()

        # AI paddle
        if self.ball_y >= Window.height - self.paddle_height - 20 and self.ai_y <= self.ball_x + 20 <= self.ai_y + self.paddle_width:
            self.ball_dy *= -1
            self.accelerate_ball()

        # AI movement (difficulty based)
        if self.ball_x > self.ai_y + self.paddle_width / 2:
            self.ai_y += min(self.ai_difficulty, Window.width - self.paddle_width - self.ai_y)
        elif self.ball_x < self.ai_y + self.paddle_width / 2:
            self.ai_y -= min(self.ai_difficulty, self.ai_y)
        self.ai.pos = (self.ai_y, Window.height - self.paddle_height - 20)

        # Player movement with keyboard
        if self.move_left:
            self.player_y -= 10
        if self.move_right:
            self.player_y += 10

        # Keep player paddle within screen bounds
        self.player_y = min(max(self.player_y, 0), Window.width - self.paddle_width)
        self.player.pos = (self.player_y, 20)

        # Scoring
        if self.ball_y <= 0:  # AI scores
            self.ai_score += 1
            self.score_label2.text = f"AI: {self.ai_score}"
            self.reset_ball()
            self.check_win_condition()
        elif self.ball_y >= Window.height:  # Player scores
            self.player_score += 1
            self.score_label1.text = f"Player: {self.player_score}"
            self.reset_ball()
            self.check_win_condition()

        # Update ball position
        self.ball.pos = (self.ball_x, self.ball_y)

        # Update high score
        self.update_high_score()

    def accelerate_ball(self):
        """Increase the speed of the ball slightly."""
        self.ball_dx *= self.ball_speed_multiplier
        self.ball_dy *= self.ball_speed_multiplier

    def update_high_score(self):
        """Update the high score if the player's score surpasses it."""
        if self.player_score > self.high_score:
            self.high_score = self.player_score
            self.high_score_label.text = f"High Score: {self.high_score}"

    def check_win_condition(self):
        """Check if either the player or the AI has won, and display a popup."""
        if self.player_score >= self.win_score:
            self.show_popup("You Win!")
        elif self.ai_score >= self.win_score:
            self.show_popup("You've been defeated!")

    def show_popup(self, message):
        """Display a popup message when the game is over."""
        layout = BoxLayout(orientation='vertical', padding=10)
        label = Label(text=message, font_size=24)
        close_button = Button(text="Return to Menu", size_hint=(1, 0.2))

        layout.add_widget(label)
        layout.add_widget(close_button)

        popup = Popup(title="Game Over", content=layout, size_hint=(0.6, 0.4))
        close_button.bind(on_release=popup.dismiss)
        popup.bind(on_dismiss=self.return_to_menu)
        popup.open()



#brick brake code starts here

class BrickBreakGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ball_x = Window.width / 2
        self.ball_y = 100
        self.ball_dx = randint(-5, 5) or 1
        self.ball_dy = 5
        self.paddle_width = 100
        self.paddle_height = 20
        self.paddle_x = Window.width / 2 - self.paddle_width / 2
        self.paddle_y = 20
        self.bricks = []
        self.brick_rows = 5
        self.brick_cols = 10
        self.brick_width = Window.width / self.brick_cols
        self.brick_height = 20
        self.ball_speed_multiplier = 1.05
        self.score = 0

        # Lives
        self.lives = 3
        self.lives_label = Label(text=f"Lives: {self.lives}", font_size=24, size_hint=(0.2, 0.1), pos_hint={'x': 0, 'y': 0.95})
        self.add_widget(self.lives_label)

        with self.canvas:
            # Create ball
            Color(1, 1, 1)
            self.ball = Ellipse(pos=(self.ball_x, self.ball_y), size=(20, 20))

            # Create paddle
            self.paddle = Rectangle(pos=(self.paddle_x, self.paddle_y), size=(self.paddle_width, self.paddle_height))

            # Create bricks
            self.brick_color = (1, 0, 0)  # Red color for bricks
            Color(*self.brick_color)
            for row in range(self.brick_rows):
                brick_row = []
                for col in range(self.brick_cols):
                    brick = Rectangle(pos=(col * self.brick_width, Window.height - (row + 1) * self.brick_height),
                                      size=(self.brick_width, self.brick_height))
                    self.canvas.add(brick)
                    brick_row.append(brick)
                self.bricks.append(brick_row)
        # Binds Keyboard inputs
        Window.bind(on_key_down=self.on_key_down)

        Window.bind(on_key_up=self.on_key_up)


        # Schedule the update method
        Clock.schedule_interval(self.update, 1.0 / 144.0)  # 144 FPS

    def update(self, dt):
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Ball collision with walls
        if self.ball_x <= 0 or self.ball_x >= Window.width - 20:
            self.ball_dx *= -1
            self.animate_ball_bounce()  # Animate the bounce on wall collision

        if self.ball_y >= Window.height - 20:
            self.ball_dy *= -1
            self.animate_ball_bounce()  # Animate the bounce on top wall

        # Ball collision with paddle
        if (self.paddle_x <= self.ball_x + 20 <= self.paddle_x + self.paddle_width) and \
           (self.paddle_y <= self.ball_y <= self.paddle_y + self.paddle_height):
            self.ball_dy *= -1
            self.ball_dx *= self.ball_speed_multiplier
            self.ball_dy *= self.ball_speed_multiplier
            self.animate_ball_bounce()  # Animate the bounce on paddle collision

        # Ball collision with bricks
        bricks_to_remove = []
        for row in self.bricks:
            for brick in row:
                if (brick.pos[0] <= self.ball_x + 20 <= brick.pos[0] + self.brick_width) and \
                   (brick.pos[1] <= self.ball_y + 20 <= brick.pos[1] + self.brick_height):
                    self.ball_dy *= -1
                    bricks_to_remove.append(brick)
                    self.animate_brick_destruction(brick)  # Animate brick destruction
                    self.score += 1
                    break
            if bricks_to_remove:
                break

        for brick in bricks_to_remove:
            self.canvas.remove(brick)
            for row in self.bricks:
                if brick in row:
                    row.remove(brick)

        # Check if all bricks are removed
        if not any(self.bricks):
            self.reset_game("You Win!")

        # Ball out of bounds: handle lives
        if self.ball_y <= 0:
            self.lives -= 1  # Decrease life
            self.lives_label.text = f"Lives: {self.lives}"  # Update label

            if self.lives <= 0:
                self.reset_game("Game Over!")
            else:
                self.reset_ball()

        # Update ball and paddle positions
        self.ball.pos = (self.ball_x, self.ball_y)
        self.paddle.pos = (self.paddle_x, self.paddle_y)

    def reset_ball(self):
        """Reset the ball position and continue the game."""
        self.ball_x = Window.width / 2
        self.ball_y = self.paddle_y + self.paddle_height + 10
        self.ball_dx = randint(-5, 5) or 1
        self.ball_dy = 5

    def reset_game(self, message):
        """Reset the game or show a Game Over screen if lives are 0."""
        if message == "Game Over!":
            self.show_game_over_popup()
        else:
            # Code to reset the game state if needed
            self.lives = 3  # Reset lives
            self.score = 0  # Reset score
            self.lives_label.text = f"Lives: {self.lives}"

    def on_touch_move(self, touch):
        """Move the paddle based on player's touch."""
        if touch.y < Window.height / 3:
            self.paddle_x = touch.x - self.paddle_width / 2
            self.paddle_x = max(0, min(Window.width - self.paddle_width, self.paddle_x))
            self.paddle.pos = (self.paddle_x, self.paddle_y)

                # Clamp the paddle position to the window bounds
        self.paddle_x = max(0, min(Window.width - self.paddle_width, self.paddle_x))
        self.paddle.pos = (self.paddle_x, self.paddle_y)
    
    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        
    # Use the first item in the keycode tuple (or just keycode if it's an integer)
        if isinstance(keycode, (list, tuple)):
            keycode = keycode[0]  # Get the first item if it's a list/tuple

        if keycode == 80:  # Left arrow key code (typically)
            self.move_left = True
        elif keycode == 79:  # Right arrow key code (typically)
            self.move_right = True

            

    def on_key_up(self, instance, keyboard, keycode):
       
    # Use the first item in the keycode tuple (or just keycode if it's an integer)
        if isinstance(keycode, (list, tuple)):
            keycode = keycode[0]  # Get the first item if it's a list/tuple

        if keycode == 80:  # Left arrow key code (typically)
            self.move_left = False
        elif keycode == 79:  # Right arrow key code (typically)
            self.move_right = False

    def animate_ball_bounce(self):
        """Animate a brief bounce effect for the ball."""
        anim = Animation(size=(30, 30), duration=0.1) + Animation(size=(20, 20), duration=0.1)
        anim.start(self.ball)

    def animate_brick_destruction(self, brick):
        """Animate a brief destruction effect for the brick."""
        anim = Animation(size=(0, 0), duration=0.1) + Animation(size=(self.brick_width, self.brick_height), duration=0.1)
        anim.start(brick)
        anim.bind(on_complete=lambda anim, brick: self.canvas.remove(brick))

    def show_game_over_popup(self):
        """Show the game-over popup when lives are 0."""
        # Stops the game from running in the background
        Clock.unschedule(self.update)
        layout = BoxLayout(orientation='vertical', padding=10)
        label = Label(text="Game Over", font_size=24)
        restart_button = Button(text="Restart", size_hint=(1, 0.2))
        close_button = Button(text="Close", size_hint=(1, 0.2))

        layout.add_widget(label)
        layout.add_widget(restart_button)
        layout.add_widget(close_button)

        popup = Popup(title="Game Over", content=layout, size_hint=(0.6, 0.4), auto_dismiss=False)

        restart_button.bind(on_release=lambda *args: self.restart_game(popup))
        close_button.bind(on_release=lambda *args: self.close_game(popup))

        popup.open()

    def restart_game(self, popup):
        """Restart the Brick Break game."""
        # Reset the game state (ball, paddle, bricks)
        self.ball_x = Window.width / 2
        self.ball_y = 100
        self.ball_dx = randint(-5, 5) or 1
        self.ball_dy = 5

        self.paddle_x = Window.width / 2 - self.paddle_width / 2

        # Rebuild the bricks
        self.bricks = []
        with self.canvas:
            Color(*self.brick_color)
            for row in range(self.brick_rows):
                brick_row = []
                for col in range(self.brick_cols):
                    brick = Rectangle(pos=(col * self.brick_width, Window.height - (row + 1) * self.brick_height),
                                      size=(self.brick_width, self.brick_height))
                    self.canvas.add(brick)
                    brick_row.append(brick)
                self.bricks.append(brick_row)

        # Reset the score and remove the popup
        self.score = 0
        popup.dismiss()

        # Reschedule the game loop
        Clock.schedule_interval(self.update, 1.0 / 144.0)

    def close_game(self, popup):
        """Close the game and return to the main menu."""
        # Stop the game loop and go back to the main menu
        Clock.unschedule(self.update)
        app = App.get_running_app()
        app.root.clear_widgets()
        popup.dismiss()
        app.root.add_widget(LaunchMenu())

    def return_to_menu(self, instance):
        """Return to the main menu when the button is clicked."""
        Clock.unschedule(self.update)  # Stop the game loop
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(LaunchMenu())


# Snake game code starts here

class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize game variables
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Snake body (list of coordinates)
        self.snake_direction = 'RIGHT'  # Initial direction
        self.block_size = 20
        self.food = (randint(1, (Window.width - 40) // 20) * 20,
                     randint(1, (Window.height - 40) // 20) * 20)  # Random food location
        self.wall_thickness = 20

        self.game_over = False

        # Initialize score variables
        self.current_score = 0
        self.high_score = 0

        # Create Labels for score display
        self.score_label = Label(text=f"Score: {self.current_score}", font_size=20, pos=(0, Window.height - 40))
        self.high_score_label = Label(text=f"High Score: {self.high_score}", font_size=20, pos=(Window.width - 150, Window.height - 40))
        
        self.add_widget(self.score_label)
        self.add_widget(self.high_score_label)

        # Bind keyboard input
        Window.bind(on_key_down=self.on_key_down)

        # Store initial touch position for detecting swipes
        self.initial_touch_pos = None

        # Schedule the update function
        Clock.schedule_interval(self.update, 1.0 / 11.0)  # Game speed (11 FPS)

    def on_touch_down(self, touch):
        """Store the initial touch position when the player touches the screen."""
        self.initial_touch_pos = touch.pos

    def on_touch_move(self, touch):
        """Detect swipe direction based on touch movement."""
        if self.initial_touch_pos:
            dx = touch.x - self.initial_touch_pos[0]  # Horizontal swipe distance
            dy = touch.y - self.initial_touch_pos[1]  # Vertical swipe distance

            # Check if the swipe is mostly horizontal or vertical
            if abs(dx) > abs(dy):  # Horizontal swipe
                if dx > 0 and self.snake_direction != 'LEFT':  # Swipe right
                    self.snake_direction = 'RIGHT'
                elif dx < 0 and self.snake_direction != 'RIGHT':  # Swipe left
                    self.snake_direction = 'LEFT'
            else:  # Vertical swipe
                if dy > 0 and self.snake_direction != 'DOWN':  # Swipe up
                    self.snake_direction = 'UP'
                elif dy < 0 and self.snake_direction != 'UP':  # Swipe down
                    self.snake_direction = 'DOWN'

        return True  # Indicate the touch was handled

    def on_touch_up(self, touch):
        """Reset the initial touch position when the player lifts the finger."""
        self.initial_touch_pos = None

    def on_key_down(self, window, keycode, scancode, text, modifiers):
        """Handle keyboard input to change the direction of the snake."""
        if keycode == 275 and self.snake_direction != 'LEFT':  # Right arrow
            self.snake_direction = 'RIGHT'
        elif keycode == 276 and self.snake_direction != 'RIGHT':  # Left arrow
            self.snake_direction = 'LEFT'
        elif keycode == 273 and self.snake_direction != 'DOWN':  # Up arrow
            self.snake_direction = 'UP'
        elif keycode == 274 and self.snake_direction != 'UP':  # Down arrow
            self.snake_direction = 'DOWN'

    def move_snake(self):
        """Move the snake based on the current direction."""
        x, y = self.snake[0]  # Current head position

        if self.snake_direction == 'RIGHT':
            new_head = (x + self.block_size, y)
        elif self.snake_direction == 'LEFT':
            new_head = (x - self.block_size, y)
        elif self.snake_direction == 'UP':
            new_head = (x, y + self.block_size)
        elif self.snake_direction == 'DOWN':
            new_head = (x, y - self.block_size)

        self.snake = [new_head] + self.snake[:-1]  # Move the snake

    def check_collision(self):
        """Check if the snake has collided with walls, boundaries, or itself."""
        head = self.snake[0]

        # Check for wall collisions (boundaries)
        if not (self.wall_thickness <= head[0] < Window.width - self.wall_thickness and
                self.wall_thickness <= head[1] < Window.height - self.wall_thickness):
            self.game_over = True

        # Check for self-collision
        if head in self.snake[1:]:
            self.game_over = True

    def check_food_collision(self):
        """Check if the snake has collided with food and grow it."""
        if self.snake[0] == self.food:
            self.snake.append(self.snake[-1])  # Grow the snake
            self.food = (randint(1, (Window.width - 40) // 20) * 20,
                         randint(1, (Window.height - 40) // 20) * 20)  # Place new food
            
            # Increase current score
            self.current_score += 1
            self.score_label.text = f"Score: {self.current_score}"

            # Update high score
            if self.current_score > self.high_score:
                self.high_score = self.current_score
                self.high_score_label.text = f"High Score: {self.high_score}"

    def update(self, dt):
        """Update the game every frame."""
        if not self.game_over:
            self.move_snake()
            self.check_collision()
            self.check_food_collision()
            self.draw()
        else:
            Clock.unschedule(self.update)
            self.show_game_over_popup()

    def draw(self):
        """Draw the snake, food, and walls on the screen."""
        self.canvas.clear()

        # Draw the snake
        with self.canvas:
            Color(0, 1, 0)  # Snake color
            for segment in self.snake:
                Rectangle(pos=segment, size=(self.block_size, self.block_size))

            # Draw the food
            Color(1, 0, 0)  # Food color
            Rectangle(pos=self.food, size=(self.block_size, self.block_size))

            # Draw walls
            Color(0, 0, 1)  # Wall color
            # Top wall
            Rectangle(pos=(0, Window.height - self.wall_thickness), size=(Window.width, self.wall_thickness))
            # Bottom wall
            Rectangle(pos=(0, 0), size=(Window.width, self.wall_thickness))
            # Left wall
            Rectangle(pos=(0, 0), size=(self.wall_thickness, Window.height))
            # Right wall
            Rectangle(pos=(Window.width - self.wall_thickness, 0), size=(self.wall_thickness, Window.height))

        self.score_label.text = f"Score: {self.current_score}"
        self.high_score_label.text = f"High Score: {self.high_score}"

    def show_game_over_popup(self):
        """Show a popup when the player loses, asking if they want to restart."""
        layout = BoxLayout(orientation='vertical', padding=10)
        label = Label(text="Game Over", font_size=24)
        restart_button = Button(text="Restart", size_hint=(1, 0.2))
        close_button = Button(text="Close", size_hint=(1, 0.2))

        layout.add_widget(label)
        layout.add_widget(restart_button)
        layout.add_widget(close_button)

        popup = Popup(title="Game Over", content=layout, size_hint=(0.6, 0.4))

        # Bind buttons to restart and close functions
        restart_button.bind(on_release=lambda *args: self.restart_game(popup))
        close_button.bind(on_release=lambda *args: self.close_game(popup))

        popup.open()

    def restart_game(self, popup):
        """Restart the game."""
        # Reset the snake, direction, and game state
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.snake_direction = 'RIGHT'
        self.food = (randint(1, (Window.width - 40) // 20) * 20,
                     randint(1, (Window.height - 40) // 20) * 20)
        self.current_score = 0
        self.score_label.text = f"Score: {self.current_score}"
        self.game_over = False

        # Close the popup
        popup.dismiss()

        # Reschedule the game loop
        Clock.schedule_interval(self.update, 1.0 / 10.0)

    def close_game(self, popup):
        """Close the game and open the main menu."""
        Clock.unschedule(self.update)  # Stop the game loop
        app = App.get_running_app()
        app.root.clear_widgets()
        popup.dismiss()
        app.root.add_widget(LaunchMenu())

        


#Main menu starts here 

class LaunchMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20

        self.add_widget(Label(text="Game Menu", font_size=32, size_hint=(1, 0.2)))
        self.add_widget(Label(text="Select AI Difficulty (for Pong)", size_hint=(1, 0.2)))

        # Difficulty slider for Pong
        self.difficulty_slider = Slider(min=1, max=10, value=5, step=1, size_hint=(1, 0.2))
        self.add_widget(self.difficulty_slider)

        # Start Pong Game Button
        start_pong_button = Button(text="Start Pong Game", size_hint=(1, 0.3))
        start_pong_button.bind(on_release=self.start_pong_game)
        self.add_widget(start_pong_button)

        # Start Brick Break Game Button
        start_brick_button = Button(text="Start Brick Break Game", size_hint=(1, 0.3))
        start_brick_button.bind(on_release=self.start_brick_game)
        self.add_widget(start_brick_button)

        # Start Snake Game Button
        start_snake_button = Button(text="Start Snake Game", size_hint=(1, 0.3))
        start_snake_button.bind(on_release=self.start_snake_game)
        self.add_widget(start_snake_button)

    def start_pong_game(self, instance):
        """Launch the Pong game."""
        self.clear_widgets()
        pong_game = PongGame(ai_difficulty=self.difficulty_slider.value)
        self.add_widget(pong_game)

    def start_brick_game(self, instance):
        """Launch the Brick Break game."""
        self.clear_widgets()
        brick_game = BrickBreakGame()
        self.add_widget(brick_game)

    def start_snake_game(self, instance):
        """Launch the Snake game."""
        self.clear_widgets()
        snake_game = SnakeGame()
        self.add_widget(snake_game)


class PongApp(App):
    def build(self):
        # Set up the window size
        Window.size = (min(Window.width, 1080), min(Window.height, 1920))
        return LaunchMenu()


if __name__ == '__main__':
    PongApp().run()