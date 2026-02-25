"""Countdown timer widget."""

from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Static


class TimerWidget(Static):
    """Displays a countdown timer with color changes."""

    remaining: reactive[int] = reactive(0)
    running: reactive[bool] = reactive(False)

    def __init__(self, seconds: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.remaining = seconds
        self._interval_handle = None

    def on_mount(self) -> None:
        self._interval_handle = self.set_interval(1, self._tick)

    def _tick(self) -> None:
        if self.running and self.remaining > 0:
            self.remaining -= 1

    def watch_remaining(self, value: int) -> None:
        self._render_display()

    def watch_running(self, value: bool) -> None:
        self._render_display()

    def _render_display(self) -> None:
        if self.remaining <= 0:
            self.update("[bold red]TIME'S UP![/]")
            self.running = False
            return

        hours = self.remaining // 3600
        minutes = (self.remaining % 3600) // 60
        seconds = self.remaining % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        if not self.running:
            self.update(f"[dim]{time_str} (paused)[/]")
        elif self.remaining < 1800:  # < 30 min
            self.update(f"[bold red]{time_str}[/]")
        elif self.remaining < 3600:  # < 1 hr
            self.update(f"[yellow]{time_str}[/]")
        else:
            self.update(f"[green]{time_str}[/]")

    def start(self) -> None:
        self.running = True

    def pause(self) -> None:
        self.running = False

    def toggle(self) -> None:
        if self.remaining > 0:
            self.running = not self.running
