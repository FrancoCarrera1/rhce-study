"""Entry point: python -m examiner [exam_file]."""

from __future__ import annotations

import sys
from pathlib import Path

from .app import ExaminerApp
from .loader import discover_exams, load_exam

# Exam directory relative to this package
_EXAMS_DIR = Path(__file__).parent / "exams"


def main() -> None:
    if len(sys.argv) > 1:
        exam_path = Path(sys.argv[1])
    else:
        # Auto-discover first exam in the built-in exams directory
        exams = discover_exams(_EXAMS_DIR)
        if not exams:
            print("No exam files found. Provide a path: python -m examiner <exam.yml>")
            sys.exit(1)
        exam_path = Path(exams[0]["path"])
        print(f"Loading: {exams[0]['title']}")

    exam = load_exam(exam_path)
    app = ExaminerApp(exam)
    app.run()


if __name__ == "__main__":
    main()
