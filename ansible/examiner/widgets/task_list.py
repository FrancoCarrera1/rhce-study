"""Sidebar task list widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import ListItem, ListView, Static

from ..models import Task, TaskStatus


_STATUS_ICONS = {
    TaskStatus.NOT_STARTED: "   ",
    TaskStatus.PARTIAL: "[yellow] ~ [/]",
    TaskStatus.PASSED: "[green] OK[/]",
    TaskStatus.FAILED: "[red] X [/]",
}


class TaskListItem(ListItem):
    """A single task entry in the sidebar."""

    def __init__(self, task: Task, index: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.exam_task = task
        self.task_index = index

    def compose(self) -> ComposeResult:
        icon = _STATUS_ICONS.get(self.exam_task.status, "   ")
        label = f"{icon} {self.task_index + 1}. {self.exam_task.title}"
        yield Static(label, markup=True)

    def refresh_status(self) -> None:
        """Re-render the status icon."""
        icon = _STATUS_ICONS.get(self.exam_task.status, "   ")
        label = f"{icon} {self.task_index + 1}. {self.exam_task.title}"
        static = self.query_one(Static)
        static.update(label)


class TaskListWidget(ListView):
    """Scrollable sidebar listing all exam tasks."""

    class TaskSelected(Message):
        """Fired when the user selects a task."""
        def __init__(self, task_id: str) -> None:
            super().__init__()
            self.task_id = task_id

    def __init__(self, tasks: list[Task], **kwargs) -> None:
        self._tasks = tasks
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        for i, task in enumerate(self._tasks):
            yield TaskListItem(task, i, id=f"task-item-{task.id}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, TaskListItem):
            self.post_message(self.TaskSelected(item.exam_task.id))

    def refresh_statuses(self) -> None:
        """Re-render all task status icons."""
        for item in self.query(TaskListItem):
            item.refresh_status()
