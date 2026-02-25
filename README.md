# Ansible Automation Study Lab

A hands-on learning environment for mastering Ansible automation on RHEL/AlmaLinux 9. Includes a TUI-based practice exam runner, 20 guided lessons, and 4 full-length practice assessments.

## What's Included

- **20 progressive lessons** covering Ansible fundamentals through advanced topics (vault, system roles, Jinja2 templates, LVM, SELinux, etc.)
- **4 practice exams** with automated verification — timed, scored, and graded against real VM state
- **TUI examiner** — a terminal app that presents tasks, runs a countdown timer, and verifies your work over SSH
- **Vagrant lab** — a multi-node AlmaLinux 9 environment (1 control + up to 5 managed nodes)

## Quick Start

```bash
# 1. Reassemble the Vagrant box (first time only)
cd Mac
cat almalinux9-vmtools.box.zip.part_* > almalinux9-vmtools.box.zip
unzip almalinux9-vmtools.box.zip
rm almalinux9-vmtools.box.zip

# 2. Start the Vagrant lab
vagrant up
cd ..

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Launch a lesson or exam
python -m examiner ansible/examiner/exams/lesson01_configuration.yml
```

See [EXAMINER.md](EXAMINER.md) for full usage, [CURRICULUM.md](CURRICULUM.md) for the learning path, and [Mac/SETUP.md](Mac/SETUP.md) for lab setup instructions.

## Troubleshooting

If a verification check is not working correctly for a given step, give [Claude](https://claude.ai) access to the project so it can review and fix the verification logic.
