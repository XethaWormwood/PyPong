from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Ellipse, Line, Color, Rectangle
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from random import randint, uniform
from math import sqrt

# Constants
ASTEROID_MIN_SPEED = 2
ASTEROID_MAX_SPEED = 2
ASTEROID_MIN_SIZE = 25
ASTEROID_MAX_SIZE = 40
BULLET_SPEED = 15
SPACESHIP_SIZE = 40
INITIAL_LIVES = 3
BULLET_COOLDOWN = 0.2
INVINCIBILITY_DURATION = 2.0
ASTEROID_SPAWN_INTERVAL = 1.2
SCORE_INCREMENT = 10

# Key mappings
KEY_UP = 'up'
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_SHOOT = 'spacebar'
KEY_PAUSE = 'p'
KEY_RESTART = 'r'

# Load sounds
shoot_sound = SoundLoader.load('shoot.wav')
explosion_sound = SoundLoader.load('explosion.wav')
background_music = SoundLoader.load('background_music.mp3')

# Play sound utility
def play_sound(sound):
    if sound:
        sound.play()
    if sound == None:
        pass


class Spaceship(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(0, 0)
        self.angle = 0
        self.thrust = 50
        self.turn_speed = 5
        self.drag = 0.78
        self.last_shot_time = 0
        self.invincible = False
        self.invincibility_timer = 1
        self.key_states = {KEY_UP: False, KEY_LEFT: False, KEY_RIGHT: False}
        with self.canvas:
            self.color = Color(0, 0, 1)
            self.shape = Line(width=2)
        self.update_shape()

    def update_shape(self):
        points = [Vector(-20, -20), Vector(0, 20), Vector(20, -20), Vector(-20, -20)]
        rotated_points = [Vector(*p).rotate(self.angle) + self.center for p in points]
        self.shape.points = [coord for point in rotated_points for coord in point]

    def move(self, dt):
        if self.key_states[KEY_UP]:
            self.accelerate()
        if self.key_states[KEY_LEFT]:
            self.rotate(1)
        if self.key_states[KEY_RIGHT]:
            self.rotate(-1)

        self.velocity *= self.drag
        self.pos = Vector(*self.pos) + self.velocity * dt
        self.wrap_around_screen()
        self.update_shape()

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
        Clock.schedule_interval(self.flash_effect, 0.1)

    def flash_effect(self, dt):
        if self.invincibility_timer > 0:
            self.color.rgb = (1, 0, 0) if self.color.rgb == (1, 0, 1) else (1, 0, 1)
            self.invincibility_timer -= dt
        else:
            self.invincible = False
            self.color.rgb = (0, 0, 1)
            Clock.unschedule(self.flash_effect)


class Asteroid(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE),) * 2
        self.speed = uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        self.angle = uniform(0, 360)
        self.velocity = Vector(self.speed, 0).rotate(self.angle)
        self.pos = (randint(0, Window.width - self.width), randint(0, Window.height - self.height))
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


class Bullet(Widget):
    def __init__(self, spaceship, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 10)
        tip_position = Vector(0, spaceship.height / 2).rotate(spaceship.angle) + spaceship.center
        self.pos = tip_position - Vector(self.width / 2, self.height / 2)
        self.velocity = Vector(0, BULLET_SPEED).rotate(spaceship.angle)
        with self.canvas:
            Color(1, 0, 0)
            self.shape = Ellipse(size=self.size, pos=self.pos)

    def move(self):
        self.pos = Vector(*self.pos) + self.velocity
        self.shape.pos = self.pos
        if not (0 <= self.x <= Window.width and 0 <= self.y <= Window.height):
            if self.parent:
                self.parent.remove_widget(self)

class Pickup(Widget):
    def __init__(self, effect, **kwargs):
        super().__init__(**kwargs)
        self.effect = effect
        self.size = (30, 30)
        self.pos = (randint(0, Window.width - self.width), randint(0, Window.height - self.height))
        with self.canvas:
            if self.effect == "health":
                Color(0, 1, 0)  # Green for health
            elif self.effect == "shield":
                Color(0, 0, 1)  # Blue for shield
            elif self.effect == "score_multiplier":
                Color(1, 1, 0)  # Yellow for score multiplier
            elif self.effect == "fire_rate":
                Color(1, 0, 1) # Purple for doubled fire rate
            self.shape = Ellipse(size=self.size, pos=self.pos)

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
 
 
class HostileAsteroid(Asteroid):
    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.target = target

    def move(self):
        # Convert target's center to a Vector
        target_position = Vector(self.target.center_x, self.target.center_y)
        # Calculate the direction toward the target
        direction = (target_position - Vector(*self.pos)).normalize()
        self.velocity = direction * self.speed
        super().move()

class AsteroidGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spaceship = Spaceship(center=(Window.width / 2, Window.height / 2))
        self.add_widget(self.spaceship)
        self.bullets = []
        self.asteroids = []
        self.pickups = []
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 50
        self.paused = False
        self.asteroid_spawn_rate = ASTEROID_SPAWN_INTERVAL
        self.current_bullet_cooldown = BULLET_COOLDOWN

        # Background setup
        with self.canvas.before:
            Color(0, 0, 0)
            self.bg = Rectangle(size=Window.size, pos=(0, 0))

        # Score and Lives Labels
        self.score_label = Label(text=f"Score: {self.score}", pos=(10, Window.height - 40), size_hint=(None, None))
        self.lives_label = Label(text=f"Lives: {self.lives}", pos=(10, Window.height - 70), size_hint=(None, None))
        self.level_label = Label(text=f"Level: {self.level}", pos=(10, Window.height - 100), size_hint=(None, None))
        self.add_widget(self.score_label)
        self.add_widget(self.lives_label)
        self.add_widget(self.level_label)

        # Scheduling game updates
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        Clock.schedule_interval(self.spawn_asteroid, self.asteroid_spawn_rate)
        Clock.schedule_interval(self.spawn_pickup, 6.0)

    def toggle_pause(self):
        self.paused = not self.paused

    def spawn_pickup(self, dt):
        if self.paused:
            return
        effect = ["health", "shield", "score_multiplier", "fire_rate"][randint(0, 3)]
        pickup = Pickup(effect)
        self.add_widget(pickup)
        self.pickups.append(pickup)

    def spawn_asteroid(self, dt):
        if self.paused:
            return
        asteroid_type = HostileAsteroid if randint(0, 4) == 0 else Asteroid
        asteroid = asteroid_type(target=self.spaceship) if asteroid_type == HostileAsteroid else Asteroid()
        if not any(self.check_collision(asteroid, obj) for obj in self.asteroids + [self.spaceship]):
            self.add_widget(asteroid)
            self.asteroids.append(asteroid)

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.lives += 1
        self.exp_to_next_level += 50
        self.asteroid_spawn_rate *= 0.9
        Clock.unschedule(self.spawn_asteroid)
        Clock.schedule_interval(self.spawn_asteroid, self.asteroid_spawn_rate)
        self.level_label.text = f"Level: {self.level}"

    def shoot_bullet(self):
        if Clock.get_time() - self.spaceship.last_shot_time >= self.current_bullet_cooldown:
            play_sound(shoot_sound)
            bullet = Bullet(self.spaceship)
            self.add_widget(bullet)
            self.bullets.append(bullet)
            self.spaceship.last_shot_time = Clock.get_time()

    def apply_fire_rate_effect(self):
        """Permanently decreases the bullet cooldown by a factor."""
        cooldown_reduction = 0.9
        self.current_bullet_cooldown *= cooldown_reduction

    def update(self, dt):
        if self.paused:
            return

        # Move spaceship
        self.spaceship.move(dt)

        # Move bullets
        for bullet in self.bullets[:]:
            bullet.move()
            # Remove bullets out of bounds
            if not (0 <= bullet.x <= Window.width and 0 <= bullet.y <= Window.height):
                self.bullets.remove(bullet)
                self.remove_widget(bullet)


        # Move asteroids
        for asteroid in self.asteroids[:]:
            asteroid.move()
            if self.check_collision(self.spaceship, asteroid):
                self.handle_collision(asteroid)

        for pickup in self.pickups[:]:
            if self.check_collision(self.spaceship, pickup):
                pickup.apply_effect(self)
                self.pickups.remove(pickup)
                self.remove_widget(pickup)

        # Handle collisions
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if self.check_collision(bullet, asteroid):
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.remove_widget(bullet)
                    self.remove_widget(asteroid)
                    play_sound(explosion_sound)
                    self.score += SCORE_INCREMENT
                    self.score_label.text = f"Score: {self.score}"
                    self.gain_exp(10)

    def handle_collision(self, asteroid):
        if not self.spaceship.invincible:
            self.lives -= 1
            self.lives_label.text = f"Lives: {self.lives}"
            self.spaceship.set_invincible(INVINCIBILITY_DURATION)
            self.remove_widget(asteroid)
            self.asteroids.remove(asteroid)
            play_sound(explosion_sound)
            if self.lives <= 0:
                self.game_over()

    def game_over(self):
        self.paused = True
        if not hasattr(self, 'game_over_label'):
            self.game_over_label = Label(
                text="Game Over! Press 'r' to Restart!",
                font_size=50,
                pos=(Window.width / 2 - 100, Window.height / 2),
                size_hint=(None, None)
            )
            self.add_widget(self.game_over_label)

    def check_collision(self, obj1, obj2):
            # Calculate the squared distance between the objects
        dx = obj1.center_x - obj2.center_x
        dy = obj1.center_y - obj2.center_y
        dist_squared = dx ** 2 + dy ** 2
    
    # Calculate the squared collision radius
        collision_radius_squared = ((obj1.width / 2) + (obj2.width / 2)) ** 2
    
    # Return True if within collision radius
        return dist_squared < collision_radius_squared

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 112:  # 'P' for pause
            self.toggle_pause()
        elif key == 32:  # Spacebar to shoot
            self.shoot_bullet()
        elif key == 273:  # Up arrow for forward thrust
            self.spaceship.key_states["up"] = True
        elif key == 276:  # Left arrow for rotation
            self.spaceship.key_states["left"] = True
        elif key == 275:  # Right arrow for rotation
            self.spaceship.key_states["right"] = True
        elif key == 114 and self.paused: # Pressing R will restart the game if its paused or Game Over
            self.restart_game()

    def on_key_up(self, window, key, scancode):
        if key == 273:  # Up arrow for forward thrust
            self.spaceship.key_states["up"] = False
        elif key == 276:  # Left arrow for rotation
            self.spaceship.key_states["left"] = False
        elif key == 275:  # Right arrow for rotation
            self.spaceship.key_states["right"] = False


    def restart_game(self):

        # Clears the Game Over Label if it exsists
        if hasattr(self, 'game_over_label'):
            self.remove_widget(self.game_over_label)
            del self.game_over_label

        # Clear existing game objects
        for bullet in self.bullets[:]:
            self.remove_widget(bullet)
        for asteroid in self.asteroids[:]:
            self.remove_widget(asteroid)
        for pickup in self.pickups[:]:
            self.remove_widget(pickup)


        self.bullets.clear()
        self.asteroids.clear()
        self.pickups.clear()

        # Reset game state
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 50
        self.paused = False
        self.asteroid_spawn_rate = ASTEROID_SPAWN_INTERVAL
        self.current_bullet_cooldown = BULLET_COOLDOWN

        # Reset labels
        self.score_label.text = f"Score: {self.score}"
        self.lives_label.text = f"Lives: {self.lives}"
        self.level_label.text = f"Level: {self.level}"

        # Reposition spaceship
        self.spaceship.center = (Window.width / 2, Window.height / 2)
        self.spaceship.velocity = Vector(0, 0)
        self.spaceship.angle = 0
        self.spaceship.update_shape()

        # Restart asteroid spawning
        Clock.unschedule(self.spawn_asteroid)
        Clock.schedule_interval(self.spawn_asteroid, self.asteroid_spawn_rate)


class AsteroidsApp(App):
    def build(self):
        game = AsteroidGame()
        Window.bind(on_key_down=game.on_key_down, on_key_up=game.on_key_up)
        return game


if __name__ == '__main__':
    AsteroidsApp().run()

