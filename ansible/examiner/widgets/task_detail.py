"""Right-panel task detail widget."""

from __future__ import annotations

from rich.text import Text

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import RichLog, Static

from ..models import CheckStatus, Exam, Task

_CHECK_ICONS = {
    CheckStatus.PENDING: "[dim]   [/]",
    CheckStatus.RUNNING: "[cyan] .. [/]",
    CheckStatus.PASSED: "[green] OK [/]",
    CheckStatus.FAILED: "[red] X  [/]",
    CheckStatus.ERROR: "[red] !! [/]",
}


class TaskDetailWidget(VerticalScroll):
    """Shows the currently selected task's description and verification results."""

    def __init__(self, exam: Exam, **kwargs) -> None:
        super().__init__(**kwargs)
        self.exam = exam
        self._current_task_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Static("", id="task-title", markup=True)
        yield Static("", id="task-description", markup=False)
        yield Static(
            "\n[bold]Verification Results[/]",
            id="results-header",
            markup=True,
        )
        yield RichLog(id="results-log", markup=True, wrap=True)

    def show_task(self, task_id: str) -> None:
        """Display a task's details and check results."""
        self._current_task_id = task_id
        task = self._find_task(task_id)
        if task is None:
            return

        title_w = self.query_one("#task-title", Static)
        title_w.update(
            f"[bold]Task {task.id}: {task.title}[/]  "
            f"[dim]({task.points} pts)[/]"
        )

        desc_w = self.query_one("#task-description", Static)
        desc_w.update(Text(f"\n{task.description}\n"))

        self._render_results(task)

    def refresh_current(self) -> None:
        """Re-render the current task's check results."""
        if self._current_task_id:
            task = self._find_task(self._current_task_id)
            if task:
                self._render_results(task)

    def _render_results(self, task: Task) -> None:
        log = self.query_one("#results-log", RichLog)
        log.clear()
        for check, result in zip(task.checks, task.results):
            icon = _CHECK_ICONS.get(result.status, "   ")
            line = f"{icon} {check.description}"
            if result.error_message and result.status in (
                CheckStatus.FAILED, CheckStatus.ERROR
            ):
                line += f"\n       [dim]{result.error_message}[/]"
            log.write(line)

    def _find_task(self, task_id: str) -> Task | None:
        for t in self.exam.tasks:
            if t.id == task_id:
                return t
        return None
