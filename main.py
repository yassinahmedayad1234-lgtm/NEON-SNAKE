import random
import json
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.core.window import Window


# NEON SNAKE 4.0 - Kivy edition
# Ported from the supplied Pygame game. Uses only Kivy drawing primitives.

BLACK = (5/255, 8/255, 24/255, 1)
WHITE = (245/255, 250/255, 1, 1)
CYAN = (0, 1, 220/255, 1)
GREEN = (0, 1, 130/255, 1)
RED = (1, 55/255, 90/255, 1)
GOLD = (1, 195/255, 25/255, 1)
PURPLE = (155/255, 65/255, 1, 1)
ORANGE = (1, 130/255, 30/255, 1)
DARK = (15/255, 22/255, 48/255, 1)
GRID = (16/255, 24/255, 45/255, 1)


class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = "menu"
        self.score = 0
        self.best = 0
        self.wallet = 0
        self.level = 1
        self.speed_ms = 140
        self.move_accum = 0
        self.enemy_accum = 0
        self.direction = (1, 0)
        self.snake = []
        self.food = None
        self.coin = None
        self.enemy = None
        self.obstacles = []
        self.stars = []
        self.skin = GREEN
        self.touch_start = None
        self.last_size = (0, 0)
        self.load_data()
        Clock.schedule_interval(self.update, 1 / 60)
        self.bind(size=self.redraw, pos=self.redraw)
        Window.bind(on_keyboard=self.on_keyboard)
        self.redraw()

    def load_data(self):
        try:
            p = Path(App.get_running_app().user_data_dir) / "snake_save.json"
            data = json.loads(p.read_text())
            self.best = int(data.get("best", 0))
            self.wallet = int(data.get("wallet", 0))
        except Exception:
            self.best = 0
            self.wallet = 0

    def save_data(self):
        try:
            p = Path(App.get_running_app().user_data_dir) / "snake_save.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"best": self.best, "wallet": self.wallet}))
        except Exception:
            pass

    def layout_values(self):
        w, h = self.width, self.height
        top = max(dp(72), h * 0.11)
        cell = max(dp(18), min(dp(30), w / 22))
        cols = max(5, int(w // cell))
        rows = max(5, int((h - top) // cell))
        board_w = cols * cell
        board_h = rows * cell
        left = self.x + (w - board_w) / 2
        bottom = self.y + (h - top - board_h) / 2
        return w, h, top, cell, cols, rows, left, bottom

    def ensure_stars(self):
        w, h, *_ = self.layout_values()
        if self.last_size != (int(w), int(h)):
            self.last_size = (int(w), int(h))
            self.stars = [[random.random() * w, random.random() * h,
                           random.randint(1, 3)] for _ in range(65)]
            if self.state == "playing":
                self.start_game()

    def random_position(self, exclude):
        _, _, _, _, cols, rows, *_ = self.layout_values()
        for _ in range(1000):
            p = (random.randrange(cols), random.randrange(rows))
            if p not in exclude:
                return p
        return None

    def start_game(self):
        _, _, _, _, cols, rows, *_ = self.layout_values()
        cx, cy = cols // 2, rows // 2
        self.snake = [(cx, cy), (max(0, cx - 1), cy), (max(0, cx - 2), cy)]
        self.direction = (1, 0)
        self.score = 0
        self.level = 1
        self.speed_ms = 140
        self.move_accum = 0
        self.enemy_accum = 0
        self.food = self.random_position(self.snake)
        self.coin = self.random_position(self.snake + [self.food])
        self.enemy = self.random_position(self.snake + [self.food, self.coin])
        self.make_obstacles()
        self.state = "playing"
        self.redraw()

    def make_obstacles(self):
        self.obstacles = []
        count = 2 + self.level * 2
        exclude = list(self.snake) + [self.food, self.coin, self.enemy]
        for _ in range(count):
            p = self.random_position(exclude + self.obstacles)
            if p is not None:
                self.obstacles.append(p)

    def change(self, dx, dy):
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)

    def move_enemy(self):
        if self.enemy is None:
            return
        _, _, _, _, cols, rows, *_ = self.layout_values()
        choices = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(choices)
        for dx, dy in choices:
            p = (self.enemy[0] + dx, self.enemy[1] + dy)
            if (0 <= p[0] < cols and 0 <= p[1] < rows and
                    p not in self.snake and p not in self.obstacles and
                    p != self.food and p != self.coin):
                self.enemy = p
                break

    def finish_game(self):
        self.best = max(self.best, self.score)
        self.save_data()
        self.state = "over"

    def update(self, dt):
        if self.width <= 0 or self.height <= 0:
            return
        self.ensure_stars()
        if self.state == "playing":
            ms = dt * 1000
            self.move_accum += ms
            self.enemy_accum += ms
            if self.enemy_accum >= 650:
                self.enemy_accum = 0
                self.move_enemy()
            if self.move_accum >= self.speed_ms:
                self.move_accum = 0
                _, _, _, _, cols, rows, *_ = self.layout_values()
                head = (self.snake[0][0] + self.direction[0],
                        self.snake[0][1] + self.direction[1])
                eating = head == self.food
                got_coin = head == self.coin
                body = self.snake if eating else self.snake[:-1]
                collision = (
                    head[0] < 0 or head[0] >= cols or
                    head[1] < 0 or head[1] >= rows or
                    head in body or head in self.obstacles or
                    head == self.enemy
                )
                if collision:
                    self.finish_game()
                else:
                    self.snake.insert(0, head)
                    if eating:
                        self.score += 10
                        self.food = self.random_position(
                            self.snake + [self.coin, self.enemy] + self.obstacles)
                        new_level = min(3, self.score // 50 + 1)
                        if new_level > self.level:
                            self.level = new_level
                            self.speed_ms = max(75, 140 - (self.level - 1) * 25)
                            self.make_obstacles()
                            self.enemy = self.random_position(
                                self.snake + [self.food, self.coin] + self.obstacles)
                    if got_coin:
                        self.wallet += 1
                        self.coin = self.random_position(
                            self.snake + [self.food, self.enemy] + self.obstacles)
                        self.save_data()
                    if not eating:
                        self.snake.pop()
        self.redraw()

    def draw_text(self, text, x, y, size, color=WHITE, center=True):
        label = CoreLabel(text=str(text), font_size=size, bold=True)
        label.refresh()
        texture = label.texture
        Color(*color)
        if center:
            Rectangle(texture=texture,
                      pos=(x - texture.width / 2, y - texture.height / 2),
                      size=texture.size)
        else:
            Rectangle(texture=texture, pos=(x, y), size=texture.size)

    def draw_button(self, text, y, color, w, h):
        bw = min(dp(300), w - dp(50))
        bh = dp(56)
        x = self.x + (w - bw) / 2
        Color(*color)
        RoundedRectangle(pos=(x, y), size=(bw, bh), radius=[dp(14)])
        Color(*WHITE)
        Line(rounded_rectangle=(x, y, bw, bh, dp(14)), width=1.2)
        self.draw_text(text, x + bw / 2, y + bh / 2, dp(20), WHITE)
        return (x, y, bw, bh)

    def redraw(self, *args):
        if self.width <= 0 or self.height <= 0:
            return
        self.ensure_stars()
        w, h, top, cell, cols, rows, left, bottom = self.layout_values()
        self.canvas.clear()
        with self.canvas:
            Color(*BLACK)
            Rectangle(pos=self.pos, size=self.size)

            # Moving star background
            for s in self.stars:
                Color(65/255, 80/255, 135/255, 1)
                Ellipse(pos=(self.x + s[0], self.y + s[1]),
                        size=(dp(s[2]), dp(s[2])))
                s[1] -= dp(s[2]) * 0.025
                if s[1] < 0:
                    s[1] = h
                    s[0] = random.random() * w

            if self.state == "menu":
                self.draw_text("NEON SNAKE", self.center_x, self.y + h * .72,
                               dp(37), CYAN)
                self.draw_text("4.0  •  ARCADE EDITION", self.center_x,
                               self.y + h * .66, dp(17), WHITE)
                self.draw_text("BEST: " + str(self.best), self.center_x,
                               self.y + h * .56, dp(22), GREEN)
                self.draw_text("COINS: " + str(self.wallet), self.center_x,
                               self.y + h * .50, dp(22), GOLD)
                self.draw_text("3 LEVELS  •  HUNTER  •  OBSTACLES",
                               self.center_x, self.y + h * .43, dp(14), WHITE)
                self.draw_button("PLAY", self.y + h * .30, CYAN, w, h)
                return

            # Header
            Color(*DARK)
            Rectangle(pos=(self.x, self.y + h - top), size=(w, top))
            self.draw_text("NEON SNAKE 4.0", self.center_x,
                           self.y + h - top * .27, dp(20), CYAN)
            self.draw_text("SCORE: " + str(self.score), self.x + w * .19,
                           self.y + h - top * .69, dp(13), WHITE)
            self.draw_text("LEVEL: " + str(self.level), self.center_x,
                           self.y + h - top * .69, dp(13), GOLD)
            self.draw_text("BEST: " + str(self.best), self.x + w * .81,
                           self.y + h - top * .69, dp(13), GREEN)

            # Grid
            Color(*GRID)
            for c in range(cols + 1):
                xx = left + c * cell
                Line(points=[xx, bottom, xx, bottom + rows * cell], width=0.6)
            for r in range(rows + 1):
                yy = bottom + r * cell
                Line(points=[left, yy, left + cols * cell, yy], width=0.6)

            # Obstacles
            for p in self.obstacles:
                Color(*ORANGE)
                RoundedRectangle(pos=(left + p[0]*cell + 2,
                                      bottom + p[1]*cell + 2),
                                 size=(cell - 4, cell - 4), radius=[dp(4)])

            # Food
            if self.food is not None:
                Color(*RED)
                Ellipse(pos=(left + self.food[0]*cell + cell/3,
                             bottom + self.food[1]*cell + cell/3),
                        size=(cell/3, cell/3))
            if self.coin is not None:
                Color(*GOLD)
                Ellipse(pos=(left + self.coin[0]*cell + cell/4,
                             bottom + self.coin[1]*cell + cell/4),
                        size=(cell/2, cell/2))
                self.draw_text("$", left + self.coin[0]*cell + cell/2,
                               bottom + self.coin[1]*cell + cell/2,
                               dp(13), WHITE)
            if self.enemy is not None:
                Color(*PURPLE)
                RoundedRectangle(pos=(left + self.enemy[0]*cell + cell/5,
                                      bottom + self.enemy[1]*cell + cell/5),
                                 size=(cell*3/5, cell*3/5), radius=[dp(4)])
                self.draw_text("!", left + self.enemy[0]*cell + cell/2,
                               bottom + self.enemy[1]*cell + cell/2,
                               dp(13), WHITE)

            # Snake with glowing-style head/body
            for i, p in enumerate(self.snake):
                Color(0, 1, .78, .18)
                RoundedRectangle(pos=(left + p[0]*cell - 2,
                                      bottom + p[1]*cell - 2),
                                 size=(cell + 4, cell + 4), radius=[dp(8)])
                Color(*(CYAN if i == 0 else self.skin))
                RoundedRectangle(pos=(left + p[0]*cell + 1,
                                      bottom + p[1]*cell + 1),
                                 size=(cell - 2, cell - 2), radius=[dp(7)])

            # Pause button
            if self.state == "playing":
                Color(*PURPLE)
                Ellipse(pos=(self.x + w - dp(54), self.y + h - top/2 - dp(15)),
                        size=(dp(30), dp(30)))
                self.draw_text("II", self.x + w - dp(39),
                               self.y + h - top/2, dp(13), WHITE)

            if self.state == "paused":
                Color(0, 0, 0, .72)
                Rectangle(pos=self.pos, size=self.size)
                self.draw_text("PAUSED", self.center_x, self.center_y + dp(80),
                               dp(34), CYAN)
                self.draw_button("RESUME", self.center_y + dp(5), GREEN, w, h)
                self.draw_button("HOME", self.center_y - dp(70), PURPLE, w, h)

            if self.state == "over":
                Color(0, 0, 0, .76)
                Rectangle(pos=self.pos, size=self.size)
                self.draw_text("GAME OVER", self.center_x,
                               self.center_y + dp(95), dp(32), RED)
                self.draw_text("SCORE: " + str(self.score), self.center_x,
                               self.center_y + dp(48), dp(21), WHITE)
                self.draw_button("PLAY AGAIN", self.center_y - dp(35), CYAN, w, h)
                self.draw_button("HOME", self.center_y - dp(105), PURPLE, w, h)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self.touch_start = touch.pos
        return True

    def on_touch_up(self, touch):
        if self.touch_start is None:
            return super().on_touch_up(touch)
        sx, sy = self.touch_start
        ex, ey = touch.pos
        dx, dy = ex - sx, ey - sy
        self.touch_start = None
        w, h, top, cell, cols, rows, left, bottom = self.layout_values()

        if self.state == "playing":
            if sy > self.y + h - top and sx > self.x + w - dp(90):
                self.state = "paused"
            elif max(abs(dx), abs(dy)) >= dp(18):
                if abs(dx) > abs(dy):
                    self.change(1 if dx > 0 else -1, 0)
                else:
                    self.change(0, 1 if dy > 0 else -1)
        else:
            tx, ty = ex, ey
            if self.state == "menu":
                if self.y + h * .30 <= ty <= self.y + h * .30 + dp(56):
                    self.start_game()
            elif self.state == "paused":
                if self.center_y + dp(5) <= ty <= self.center_y + dp(61):
                    self.state = "playing"
                elif self.center_y - dp(70) <= ty <= self.center_y - dp(14):
                    self.state = "menu"
            elif self.state == "over":
                if self.center_y - dp(35) <= ty <= self.center_y + dp(21):
                    self.start_game()
                elif self.center_y - dp(105) <= ty <= self.center_y - dp(49):
                    self.state = "menu"
        self.redraw()
        return True

    def on_keyboard(self, window, key, *args):
        if key == 27:
            if self.state == "playing":
                self.state = "paused"
            elif self.state == "paused":
                self.state = "playing"
            else:
                self.state = "menu"
            self.redraw()
            return True
        return False


class NeonSnakeApp(App):
    title = "NEON SNAKE"

    def build(self):
        Window.clearcolor = BLACK
        return SnakeGame()


if __name__ == "__main__":
    NeonSnakeApp().run()
