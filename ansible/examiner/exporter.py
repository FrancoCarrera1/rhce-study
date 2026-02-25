"""Export exam results and student playbooks to a markdown grade report."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import CheckStatus, Exam, TaskStatus
from .verification.ssh import SSHConnectionPool

RESULTS_DIR = Path(__file__).parent / "results"

# File extensions to language hints for markdown code blocks
_LANG_MAP = {"yml": "yaml", "yaml": "yaml", "cfg": "ini", "j2": "jinja2", "conf": "ini"}


async def export_grade_report(exam: Exam, pool: SSHConnectionPool) -> Path:
    """Generate a markdown grade report with scores, check details, and playbook contents."""
    RESULTS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filepath = RESULTS_DIR / f"{exam.id}_{timestamp}.md"

    lines: list[str] = []

    # ── Header ──
    pct = exam.score_percent
    passed = pct >= exam.passing_score
    lines.append(f"# Grade Report: {exam.title}")
    lines.append("")
    lines.append(f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- **Score:** {exam.earned_points:.1f} / {exam.total_points:.1f} ({pct:.0f}%)")
    lines.append(f"- **Result:** {'PASS' if passed else 'FAIL'} (need {exam.passing_score}%)")
    lines.append("")

    # Quick summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Task | Title | Points | Status |")
    lines.append("|------|-------|--------|--------|")
    for task in exam.tasks:
        s = task.status
        icon = {"passed": "PASS", "partial": "PARTIAL", "failed": "FAIL"}.get(s.value, "-")
        lines.append(f"| {task.id} | {task.title} | {task.earned_points:.1f}/{task.points:.1f} | {icon} |")
    lines.append("")

    # ── Per-task detail ──
    lines.append("## Detailed Results")
    lines.append("")

    _STATUS_LABEL = {
        CheckStatus.PASSED: "OK",
        CheckStatus.FAILED: "FAIL",
        CheckStatus.ERROR: "ERROR",
        CheckStatus.PENDING: "-",
        CheckStatus.RUNNING: "...",
    }

    for task in exam.tasks:
        status_label = {
            TaskStatus.PASSED: "PASS",
            TaskStatus.PARTIAL: "PARTIAL",
            TaskStatus.FAILED: "FAIL",
            TaskStatus.NOT_STARTED: "NOT GRADED",
        }.get(task.status, task.status.value)

        lines.append(
            f"### Task {task.id}: {task.title} "
            f"({task.earned_points:.1f}/{task.points:.1f} pts) — {status_label}"
        )
        lines.append("")
        lines.append("| Check | Description | Result | Details |")
        lines.append("|-------|-------------|--------|---------|")
        for check, result in zip(task.checks, task.results):
            r = _STATUS_LABEL.get(result.status, result.status.value)
            details = (result.error_message or "").replace("|", "\\|")
            lines.append(f"| {check.id} | {check.description} | {r} | {details} |")
        lines.append("")

    # ── Student playbooks from control node ──
    lines.append("---")
    lines.append("")
    lines.append("## Student Playbooks")
    lines.append("")

    control = exam.hosts.get("control")
    if control:
        try:
            rc, file_list = await pool.run_command(
                "control",
                control.ip,
                f"find {exam.working_dir} -maxdepth 5 -type f "
                "\\( -name '*.yml' -o -name '*.yaml' -o -name '*.cfg' "
                "-o -name '*.j2' -o -name 'inventory' -o -name '*.conf' \\) "
                "! -path '*/examiner/*' ! -path '*/.git/*' "
                "2>/dev/null | sort",
                control.ssh_user,
            )
            if rc == 0 and file_list.strip():
                for remote_path in file_list.strip().splitlines():
                    remote_path = remote_path.strip()
                    if not remote_path:
                        continue
                    rc2, content = await pool.run_command(
                        "control", control.ip, f"cat '{remote_path}'", control.ssh_user
                    )
                    ext = remote_path.rsplit(".", 1)[-1] if "." in remote_path else ""
                    lang = _LANG_MAP.get(ext, "")
                    lines.append(f"### `{remote_path}`")
                    lines.append("")
                    lines.append(f"```{lang}")
                    lines.append(content.rstrip() if rc2 == 0 else f"# Error reading file: rc={rc2}")
                    lines.append("```")
                    lines.append("")
            else:
                lines.append("*No playbook files found on control node.*")
                lines.append("")
        except Exception as e:
            lines.append(f"*Error connecting to control node: {e}*")
            lines.append("")

    # ── Reference Solutions ──
    if exam.solutions_file and Path(exam.solutions_file).exists():
        lines.append("---")
        lines.append("")
        lines.append("## Reference Solutions")
        lines.append("")
        lines.append(Path(exam.solutions_file).read_text())

    filepath.write_text("\n".join(lines))
    return filepath
