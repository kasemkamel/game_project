# core/game_loop.py
import time

class GameLoop:
    def __init__(self):
        # Handler lists
        self.fast_tick_handlers = []  # e.g., movement, rendering updates
        self.slow_tick_handlers = []  # e.g., economic/happiness systems

        # Timing
        self.last_fast_tick = time.time()
        self.last_slow_tick = time.time()

        # Intervals
        self.fast_interval = 1 / 20          # 20 Hz
        self.slow_interval = 4 * 60          # 4 minutes (in seconds)

        # Counters for delta accumulation
        self.fast_accumulator = 0.0
        self.slow_accumulator = 0.0

    def register_fast_tick(self, func):
        """Register function to be called every fast tick."""
        self.fast_tick_handlers.append(func)

    def register_slow_tick(self, func):
        """Register function to be called every slow tick."""
        self.slow_tick_handlers.append(func)

    def update(self, dt):
        """Called once per frame, accumulates delta time for each tick system."""
        now = time.time()

        # --- FAST TICK (20Hz) ---
        self.fast_accumulator += dt
        while self.fast_accumulator >= self.fast_interval:
            for func in self.fast_tick_handlers:
                func(self.fast_interval)
            self.fast_accumulator -= self.fast_interval

        # --- SLOW TICK (4 minutes) ---
        self.slow_accumulator += dt
        if self.slow_accumulator >= self.slow_interval:
            for func in self.slow_tick_handlers:
                func()
            print("[SLOW TICK] Triggered at", time.strftime("%H:%M:%S"))
            self.slow_accumulator = 0.0
