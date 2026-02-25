"""Verification runner — executes checks against VMs."""

from __future__ import annotations

from ..models import Check, CheckResult, CheckStatus, Exam, Task
from .ssh import SSHConnectionPool


class VerificationRunner:
    """Runs verification checks over SSH and records results."""

    def __init__(self, pool: SSHConnectionPool, exam: Exam) -> None:
        self.pool = pool
        self.exam = exam

    def _resolve_ip(self, node_name: str) -> str:
        """Look up the IP for a node from the exam host definitions."""
        host = self.exam.hosts.get(node_name)
        if host is None:
            raise ValueError(f"Unknown host: {node_name}")
        return host.ip

    def _resolve_user(self, node_name: str) -> str:
        host = self.exam.hosts.get(node_name)
        if host is None:
            return "vagrant"
        return host.ssh_user

    async def verify_check(self, check: Check, result: CheckResult) -> None:
        """Run a single check and update the result in-place."""
        result.status = CheckStatus.RUNNING
        result.error_message = None
        try:
            ip = self._resolve_ip(check.node)
            user = self._resolve_user(check.node)
            rc, stdout = await self.pool.run_command(
                check.node, ip, check.command, user
            )
            result.actual_rc = rc
            result.actual_stdout = stdout.strip()

            # Evaluate — all conditions must pass
            passed = True

            if check.expect_rc is not None:
                if rc != check.expect_rc:
                    passed = False
                    result.error_message = (
                        f"Expected rc={check.expect_rc}, got {rc}"
                    )

            if passed and check.expect_stdout is not None:
                if result.actual_stdout != check.expect_stdout.strip():
                    passed = False
                    result.error_message = (
                        f"Expected stdout '{check.expect_stdout.strip()}', "
                        f"got '{result.actual_stdout}'"
                    )

            if passed and check.expect_stdout_contains is not None:
                if check.expect_stdout_contains not in (result.actual_stdout or ""):
                    passed = False
                    result.error_message = (
                        f"stdout missing '{check.expect_stdout_contains}'"
                    )

            result.status = CheckStatus.PASSED if passed else CheckStatus.FAILED

        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error_message = str(e)

    async def verify_task(self, task: Task) -> None:
        """Run all checks for a task sequentially."""
        task.init_results()
        for check, result in zip(task.checks, task.results):
            await self.verify_check(check, result)

    async def verify_all(self) -> None:
        """Run verification for every task."""
        for task in self.exam.tasks:
            await self.verify_task(task)

    def reset_task(self, task: Task) -> None:
        """Reset all results for a task to PENDING."""
        for result in task.results:
            result.status = CheckStatus.PENDING
            result.actual_rc = None
            result.actual_stdout = None
            result.error_message = None

    def reset_all(self) -> None:
        """Reset all tasks."""
        for task in self.exam.tasks:
            self.reset_task(task)
