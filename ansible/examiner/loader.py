"""YAML exam loader."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import Check, Exam, HostDef, Task


def load_exam(path: str | Path) -> Exam:
    """Parse a YAML exam file and return an Exam model."""
    path = Path(path)
    with open(path) as f:
        data = yaml.safe_load(f)

    hosts: dict[str, HostDef] = {}
    for name, hdata in data.get("hosts", {}).items():
        hosts[name] = HostDef(
            name=name,
            hostname=hdata.get("hostname", name),
            ip=hdata["ip"],
            ssh_user=hdata.get("ssh_user", "vagrant"),
            groups=hdata.get("groups", []),
        )

    tasks: list[Task] = []
    for tdata in data.get("tasks", []):
        checks: list[Check] = []
        for cdata in tdata.get("checks", []):
            checks.append(Check(
                id=cdata["id"],
                description=cdata["description"],
                node=cdata["node"],
                command=cdata["command"],
                expect_rc=cdata.get("expect_rc", 0),
                expect_stdout=cdata.get("expect_stdout"),
                expect_stdout_contains=cdata.get("expect_stdout_contains"),
            ))
        tasks.append(Task(
            id=tdata["id"],
            title=tdata["title"],
            points=float(tdata.get("points", 1)),
            description=tdata["description"],
            checks=checks,
        ))

    # Resolve solutions_file relative to YAML directory
    solutions_file = data.get("solutions_file")
    if solutions_file:
        solutions_file = str((path.parent / solutions_file).resolve())

    return Exam(
        id=data.get("id", path.stem),
        title=data.get("title", "Untitled Exam"),
        duration=int(data.get("duration", 14400)),
        passing_score=float(data.get("passing_score", 70)),
        hosts=hosts,
        tasks=tasks,
        working_dir=data.get("working_dir", "/home/vagrant/ansible"),
        solutions_file=solutions_file,
    )


def discover_exams(directory: str | Path) -> list[dict]:
    """List available exam YAML files in a directory."""
    directory = Path(directory)
    exams = []
    for p in sorted(directory.glob("*.yml")):
        try:
            with open(p) as f:
                data = yaml.safe_load(f)
            exams.append({
                "path": str(p),
                "id": data.get("id", p.stem),
                "title": data.get("title", p.stem),
            })
        except Exception:
            continue
    return exams
