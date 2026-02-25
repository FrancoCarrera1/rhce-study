"""Main Textual application for the Ansible practice exam."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Static
from textual import work

from .exporter import export_grade_report
from .models import Exam
from .verification.runner import VerificationRunner
from .verification.ssh import SSHConnectionPool
from .widgets.task_detail import TaskDetailWidget
from .widgets.task_list import TaskListWidget
from .widgets.timer import TimerWidget


class ExaminerApp(App):
    """Ansible Practice Exam TUI."""

    CSS_PATH = "app.tcss"
    TITLE = "Ansible Examiner"

    BINDINGS = [
        Binding("v", "verify_current", "Verify Task"),
        Binding("V", "verify_all", "Verify All", key_display="shift+v"),
        Binding("r", "reset_current", "Reset Task"),
        Binding("R", "reset_all", "Reset All", key_display="shift+r"),
        Binding("t", "toggle_timer", "Timer"),
        Binding("c", "check_connectivity", "Connectivity"),
        Binding("e", "export_report", "Export"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, exam: Exam) -> None:
        super().__init__()
        self.exam = exam
        self.pool = SSHConnectionPool()
        self.runner = VerificationRunner(self.pool, exam)
        self._current_task_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Static(f"[bold]{self.exam.title}[/]", id="status-title", markup=True),
            TimerWidget(self.exam.duration, id="status-timer"),
            Static(self._score_text(), id="status-score", markup=True),
            id="status-bar",
        )
        yield Horizontal(
            TaskListWidget(self.exam.tasks, id="task-sidebar"),
            TaskDetailWidget(self.exam, id="task-detail"),
            id="main-content",
        )
        yield Footer()

    def on_mount(self) -> None:
        if self.exam.tasks:
            first = self.exam.tasks[0]
            self._current_task_id = first.id
            self.query_one(TaskDetailWidget).show_task(first.id)
        timer = self.query_one(TimerWidget)
        timer.start()

    # ── Task navigation ──

    def on_task_list_widget_task_selected(
        self, event: TaskListWidget.TaskSelected
    ) -> None:
        self._current_task_id = event.task_id
        self.query_one(TaskDetailWidget).show_task(event.task_id)

    # ── Score display ──

    def _score_text(self) -> str:
        earned = self.exam.earned_points
        total = self.exam.total_points
        pct = self.exam.score_percent
        passing = self.exam.passing_score
        color = "green" if pct >= passing else "red" if pct > 0 else "dim"
        return f"[{color}]{earned:.1f}/{total:.1f} ({pct:.0f}%)[/]"

    def _refresh_score(self) -> None:
        self.query_one("#status-score", Static).update(self._score_text())

    # ── Actions ──

    def action_verify_current(self) -> None:
        if self._current_task_id:
            self._run_verify_task(self._current_task_id)

    def action_verify_all(self) -> None:
        self._run_verify_all()

    def action_reset_current(self) -> None:
        task = self._find_task(self._current_task_id)
        if task:
            self.runner.reset_task(task)
            self._refresh_ui()

    def action_reset_all(self) -> None:
        self.runner.reset_all()
        self._refresh_ui()

    def action_toggle_timer(self) -> None:
        self.query_one(TimerWidget).toggle()

    def action_check_connectivity(self) -> None:
        self._run_connectivity_check()

    def action_export_report(self) -> None:
        self._run_export()

    # ── Async workers ──

    @work(exclusive=True, group="verify")
    async def _run_verify_task(self, task_id: str) -> None:
        task = self._find_task(task_id)
        if task is None:
            return
        self.notify(f"Verifying: {task.title}...")
        await self.runner.verify_task(task)
        self._refresh_ui()
        status = task.status.value
        self.notify(f"Task {task.id}: {status}")

    @work(exclusive=True, group="verify")
    async def _run_verify_all(self) -> None:
        self.notify("Verifying all tasks...")
        for task in self.exam.tasks:
            await self.runner.verify_task(task)
            self._refresh_ui()
        pct = self.exam.score_percent
        self.notify(f"Verification complete — Score: {pct:.0f}%")

    @work(exclusive=True, group="verify")
    async def _run_connectivity_check(self) -> None:
        self.notify("Testing VM connectivity...")
        results = []
        for name, host in self.exam.hosts.items():
            ok, msg = await self.pool.test_connectivity(name, host.ip, host.ssh_user)
            status = "[green]OK[/]" if ok else "[red]FAIL[/]"
            results.append(f"{status} {name} ({host.ip}): {msg}")
        # Show results in the detail panel via the results log
        detail = self.query_one(TaskDetailWidget)
        log = detail.query_one("#results-log")
        log.clear()
        log.write("[bold]VM Connectivity Check[/]\n")
        for line in results:
            log.write(line)
        self.notify("Connectivity check complete")

    @work(exclusive=True, group="export")
    async def _run_export(self) -> None:
        self.notify("Exporting grade report...")
        try:
            path = await export_grade_report(self.exam, self.pool)
            self.notify(f"Report saved: {path}", timeout=10)
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")

    # ── Helpers ──

    def _find_task(self, task_id: str | None):
        if task_id is None:
            return None
        for t in self.exam.tasks:
            if t.id == task_id:
                return t
        return None

    def _refresh_ui(self) -> None:
        self.query_one(TaskListWidget).refresh_statuses()
        self.query_one(TaskDetailWidget).refresh_current()
        self._refresh_score()

    async def on_unmount(self) -> None:
        await self.pool.close_all()
