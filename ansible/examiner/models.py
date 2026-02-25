"""Data models for the examiner."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CheckStatus(Enum):
    """Status of a single verification check."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


class TaskStatus(Enum):
    """Computed status of a task based on its check results."""
    NOT_STARTED = "not_started"
    PARTIAL = "partial"
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class Check:
    """A single verification check — run a command on a node, assert the result."""
    id: str
    description: str
    node: str
    command: str
    expect_rc: int | None = 0
    expect_stdout: str | None = None
    expect_stdout_contains: str | None = None


@dataclass
class CheckResult:
    """Result of running a single check."""
    check_id: str
    status: CheckStatus = CheckStatus.PENDING
    actual_rc: int | None = None
    actual_stdout: str | None = None
    error_message: str | None = None


@dataclass
class HostDef:
    """A host defined in the exam YAML."""
    name: str
    hostname: str
    ip: str
    ssh_user: str = "vagrant"
    groups: list[str] = field(default_factory=list)


@dataclass
class Task:
    """An exam task with multiple verification checks."""
    id: str
    title: str
    points: float
    description: str
    checks: list[Check] = field(default_factory=list)
    results: list[CheckResult] = field(default_factory=list)

    def init_results(self) -> None:
        """Create a CheckResult for each check if not already present."""
        if len(self.results) != len(self.checks):
            self.results = [
                CheckResult(check_id=c.id) for c in self.checks
            ]

    @property
    def status(self) -> TaskStatus:
        if not self.results or all(
            r.status == CheckStatus.PENDING for r in self.results
        ):
            return TaskStatus.NOT_STARTED
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASSED)
        if passed == len(self.checks):
            return TaskStatus.PASSED
        if passed > 0:
            return TaskStatus.PARTIAL
        return TaskStatus.FAILED

    @property
    def earned_points(self) -> float:
        """Partial credit: fraction of checks passed * points."""
        if not self.checks:
            return 0.0
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASSED)
        return self.points * (passed / len(self.checks))


@dataclass
class Exam:
    """A complete practice exam."""
    id: str
    title: str
    duration: int  # seconds
    passing_score: float  # percent 0-100
    hosts: dict[str, HostDef] = field(default_factory=dict)
    tasks: list[Task] = field(default_factory=list)
    working_dir: str = "/home/vagrant/ansible"
    solutions_file: str | None = None

    def __post_init__(self) -> None:
        for task in self.tasks:
            task.init_results()

    @property
    def total_points(self) -> float:
        return sum(t.points for t in self.tasks)

    @property
    def earned_points(self) -> float:
        return sum(t.earned_points for t in self.tasks)

    @property
    def score_percent(self) -> float:
        if self.total_points == 0:
            return 0.0
        return (self.earned_points / self.total_points) * 100
