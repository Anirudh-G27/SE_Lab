import array
import math

import pygame
from .marble import Marble
from .wall import Wall

# Game Engine

WHITE = (255, 255, 255)
DARK = (40, 40, 50)
WALL_COLOR = (90, 90, 110)
GOAL_COLOR = (60, 200, 120)
LOSE_COLOR = (230, 90, 90)
PANEL_COLOR = (30, 30, 42)
PANEL_BORDER = (110, 110, 140)
BUTTON_COLOR = (70, 70, 95)
BUTTON_HOVER = (105, 105, 145)
BUTTON_DISABLED = (50, 50, 62)
TEXT_DIM = (170, 170, 190)

# Medium matches the original game's settings.
DIFFICULTIES = {
    "easy":   {"label": "Easy",   "tilt_strength": 0.5, "friction": 0.04,  "time_limit_ms": 60000},
    "medium": {"label": "Medium", "tilt_strength": 0.6, "friction": 0.02,  "time_limit_ms": 45000},
    "hard":   {"label": "Hard",   "tilt_strength": 0.8, "friction": 0.008, "time_limit_ms": 30000},
}

KEY_ACTIONS = {
    pygame.K_1: "easy", pygame.K_KP1: "easy", pygame.K_e: "easy",
    pygame.K_2: "medium", pygame.K_KP2: "medium", pygame.K_m: "medium",
    pygame.K_3: "hard", pygame.K_KP3: "hard", pygame.K_h: "hard",
    pygame.K_ESCAPE: "exit", pygame.K_q: "exit",
}

START_POS = (50, 50)
WALL_RESTITUTION = 0.3          # fraction of speed kept (reversed) after a bounce
BOUNCE_SOUND_MIN_IMPACT = 1.5   # ignore tiny contacts (e.g. resting against a wall)
END_INPUT_DELAY_MS = 500        # avoids skipping the end screen by accident


class SoundManager:
    """Generates simple sound effects in code (no audio files required).

    If audio is unavailable (no sound device, unsupported mixer format),
    every play_* method silently does nothing so the game still runs.
    """

    BOUNCE_COOLDOWN_MS = 60

    def __init__(self):
        self.enabled = False
        self.bounce = None
        self.goal = None
        self.timeout = None
        self._last_bounce_ms = -1000

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            mixer_state = pygame.mixer.get_init()
            if mixer_state is None:
                return
            self.rate, fmt, self.channels = mixer_state
            if fmt != -16:  # only signed 16-bit is supported by the generator
                return

            # short low thud
            self.bounce = self._make_sound([(220, 110, 0.08, "sine", 0.6)])
            # rising arpeggio C5 E5 G5 C6
            self.goal = self._make_sound([
                (523.25, 523.25, 0.12, "sine", 0.45),
                (659.25, 659.25, 0.12, "sine", 0.45),
                (783.99, 783.99, 0.12, "sine", 0.45),
                (1046.50, 1046.50, 0.30, "sine", 0.45),
            ])
            # falling "buzzer"
            self.timeout = self._make_sound([
                (440, 440, 0.18, "square", 0.25),
                (349, 349, 0.18, "square", 0.25),
                (262, 262, 0.40, "square", 0.25),
            ])
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def _make_sound(self, notes):
        samples = array.array("h")
        for f0, f1, duration, wave, volume in notes:
            samples.extend(self._tone(f0, f1, duration, wave, volume))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _tone(self, f0, f1, duration, wave, volume):
        total = max(1, int(self.rate * duration))
        attack = max(1, int(self.rate * 0.005))
        out = array.array("h")
        phase = 0.0
        for i in range(total):
            t = i / total
            freq = f0 + (f1 - f0) * t
            phase += 2 * math.pi * freq / self.rate
            s = math.sin(phase)
            if wave == "square":
                s = 1.0 if s >= 0 else -1.0
            envelope = min(1.0, i / attack) * (1.0 - t)
            value = int(32767 * volume * envelope * s)
            for _ in range(self.channels):
                out.append(value)
        return out

    def play_bounce(self, strength=1.0):
        """strength is 0..1 and scales the volume."""
        if not self.enabled:
            return
        now = pygame.time.get_ticks()
        if now - self._last_bounce_ms < self.BOUNCE_COOLDOWN_MS:
            return
        self._last_bounce_ms = now
        self.bounce.set_volume(0.3 + 0.7 * max(0.0, min(1.0, strength)))
        self.bounce.play()

    def play_goal(self):
        if self.enabled:
            self.goal.play()

    def play_timeout(self):
        if self.enabled:
            self.timeout.play()


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.max_speed = 9

        self.walls = self._build_maze()
        self.goal_x, self.goal_y, self.goal_radius = width - 60, height - 60, 22

        self.font = pygame.font.SysFont("Arial", 26)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.sounds = SoundManager()

        self._build_end_screen_layout()

        self.marble = Marble(*START_POS)
        self.difficulty = "medium"
        self.reset(self.difficulty)

    # ------------------------------------------------------------------
    # Setup / reset
    # ------------------------------------------------------------------

    def reset(self, difficulty=None):
        """Start a fresh round, optionally switching difficulty."""
        if difficulty is not None:
            self.difficulty = difficulty
        settings = DIFFICULTIES[self.difficulty]

        self.tilt_strength = settings["tilt_strength"]
        self.friction = settings["friction"]
        self.time_limit_ms = settings["time_limit_ms"]

        self.marble.reset(*START_POS)

        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_ms = 0
        self.game_over = False
        self.result = None  # "solved" or "timeout"
        self.finish_time_ms = None
        self.game_over_ticks = 0

    def _build_maze(self):
        walls = []
        t = 16  # wall thickness

        # outer boundary
        walls.append(Wall(0, 0, self.width, t))
        walls.append(Wall(0, self.height - t, self.width, t))
        walls.append(Wall(0, 0, t, self.height))
        walls.append(Wall(self.width - t, 0, t, self.height))

        # a few internal walls forming a simple winding path
        walls.append(Wall(0, 140, self.width - 140, t))
        walls.append(Wall(140, 260, self.width - 140, t))
        walls.append(Wall(0, 380, self.width - 140, t))

        return walls

    def _build_end_screen_layout(self):
        panel_w, panel_h = 460, 320
        self.panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        self.panel_rect.center = (self.width // 2, self.height // 2)

        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 170))

        btn_w, btn_h, gap = 130, 64, 15
        total = 3 * btn_w + 2 * gap
        x = self.panel_rect.centerx - total // 2
        y = self.panel_rect.y + 190

        self.buttons = {}
        for name in ("easy", "medium", "hard"):
            self.buttons[name] = pygame.Rect(x, y, btn_w, btn_h)
            x += btn_w + gap

        exit_rect = pygame.Rect(0, 0, 200, 40)
        exit_rect.midtop = (self.panel_rect.centerx, y + btn_h + 12)
        self.buttons["exit"] = exit_rect

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _end_screen_active(self):
        return (self.game_over and
                pygame.time.get_ticks() - self.game_over_ticks >= END_INPUT_DELAY_MS)

    def handle_event(self, event):
        # Gameplay is driven by the continuous mouse position (see
        # handle_input). Events only matter on the end screen.
        if not self._end_screen_active():
            return None

        action = None
        if event.type == pygame.KEYDOWN:
            action = KEY_ACTIONS.get(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    action = name
                    break

        if action == "exit":
            return "QUIT"
        if action in DIFFICULTIES:
            self.reset(action)
        return None

    def handle_input(self):
        if self.game_over:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.width // 2
        dy = mouse_y - self.height // 2
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        ax = (dx / dist) * self.tilt_strength
        ay = (dy / dist) * self.tilt_strength
        self.marble.vx += ax
        self.marble.vy += ay

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _end_round(self, result):
        self.game_over = True
        self.result = result
        self.game_over_ticks = pygame.time.get_ticks()
        if result == "solved":
            self.finish_time_ms = self.elapsed_ms
            self.sounds.play_goal()
        else:
            self.sounds.play_timeout()

    def update(self):
        if self.game_over:
            return None

        elapsed = pygame.time.get_ticks() - self.start_ticks
        if elapsed >= self.time_limit_ms:
            self.elapsed_ms = self.time_limit_ms
            self._end_round("timeout")
            return None
        self.elapsed_ms = elapsed

        self.marble.vx *= (1 - self.friction)
        self.marble.vy *= (1 - self.friction)

        speed = (self.marble.vx ** 2 + self.marble.vy ** 2) ** 0.5
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.marble.vx *= scale
            self.marble.vy *= scale

        self.marble.x += self.marble.vx
        self.marble.y += self.marble.vy

        self._resolve_wall_collisions()

        gx = self.goal_x - self.marble.x
        gy = self.goal_y - self.marble.y
        if (gx ** 2 + gy ** 2) ** 0.5 <= self.goal_radius:
            self._end_round("solved")

        return None

    def _resolve_wall_collisions(self):
        """Exact circle-vs-rectangle collision.

        For each wall, find the point on the rectangle closest to the
        marble's centre. The marble touches the wall only if that point is
        closer than the marble's radius. The marble is pushed out along the
        contact normal and only the velocity component pointing into the
        wall is reflected, so near a corner it bounces off the corner
        itself (not off empty space) and slides naturally along flat sides.
        """
        m = self.marble
        r = m.radius
        strongest_impact = 0.0

        for wall in self.walls:
            cx, cy = wall.closest_point(m.x, m.y)
            dx = m.x - cx
            dy = m.y - cy
            dist_sq = dx * dx + dy * dy

            if dist_sq >= r * r:
                continue  # circle does not touch this wall

            if dist_sq > 1e-12:
                dist = math.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist
                penetration = r - dist
            else:
                # Centre is inside the wall (e.g. after a very fast move):
                # leave through the nearest face.
                faces = [
                    (m.x - wall.left, -1, 0),
                    (wall.right - m.x, 1, 0),
                    (m.y - wall.top, 0, -1),
                    (wall.bottom - m.y, 0, 1),
                ]
                depth, nx, ny = min(faces, key=lambda f: f[0])
                penetration = depth + r

            m.x += nx * penetration
            m.y += ny * penetration

            vn = m.vx * nx + m.vy * ny  # velocity along the normal
            if vn < 0:  # moving into the wall
                m.vx -= (1 + WALL_RESTITUTION) * vn * nx
                m.vy -= (1 + WALL_RESTITUTION) * vn * ny
                strongest_impact = max(strongest_impact, -vn)

        if strongest_impact >= BOUNCE_SOUND_MIN_IMPACT:
            self.sounds.play_bounce(strongest_impact / self.max_speed)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _blit_centered(self, surface, text, font, color, center):
        img = font.render(text, True, color)
        surface.blit(img, img.get_rect(center=center))

    def render(self, screen):
        screen.fill(DARK)

        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall.rect())

        pygame.draw.circle(screen, GOAL_COLOR, (self.goal_x, self.goal_y), self.goal_radius)
        pygame.draw.circle(screen, WHITE, (int(self.marble.x), int(self.marble.y)), self.marble.radius)

        # Timer is always visible; it freezes when the round ends.
        remaining_ms = max(0, self.time_limit_ms - self.elapsed_ms)
        seconds_left = (remaining_ms + 999) // 1000
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (24, 24))

        if self.game_over:
            self._render_end_screen(screen)

    def _render_end_screen(self, screen):
        screen.blit(self.overlay, (0, 0))

        panel = self.panel_rect
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=12)
        pygame.draw.rect(screen, PANEL_BORDER, panel, width=2, border_radius=12)

        cx = panel.centerx
        if self.result == "solved":
            self._blit_centered(screen, "Maze Solved!", self.title_font, GOAL_COLOR, (cx, panel.y + 45))
            detail = f"Finished in {self.finish_time_ms / 1000:.1f}s"
        else:
            self._blit_centered(screen, "Time's Up!", self.title_font, LOSE_COLOR, (cx, panel.y + 45))
            detail = "The maze was not solved in time."
        self._blit_centered(screen, detail, self.font, WHITE, (cx, panel.y + 100))

        label = DIFFICULTIES[self.difficulty]["label"]
        self._blit_centered(screen, f"Difficulty: {label}", self.small_font, TEXT_DIM, (cx, panel.y + 135))
        self._blit_centered(screen, "Play again - choose a difficulty:", self.small_font, WHITE,
                            (cx, panel.y + 168))

        active = self._end_screen_active()
        mouse_pos = pygame.mouse.get_pos()

        for name, rect in self.buttons.items():
            if not active:
                color = BUTTON_DISABLED
            elif rect.collidepoint(mouse_pos):
                color = BUTTON_HOVER
            else:
                color = BUTTON_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=8)

            text_color = WHITE if active else TEXT_DIM
            if name == "exit":
                self._blit_centered(screen, "[Esc] Exit", self.font, text_color, rect.center)
            else:
                info = DIFFICULTIES[name]
                number = list(DIFFICULTIES).index(name) + 1
                self._blit_centered(screen, f"[{number}] {info['label']}", self.font, text_color,
                                    (rect.centerx, rect.y + 24))
                self._blit_centered(screen, f"{info['time_limit_ms'] // 1000}s", self.small_font,
                                    TEXT_DIM, (rect.centerx, rect.y + 47))