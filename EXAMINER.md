# Examiner — Ansible Practice Exam TUI

A terminal-based practice exam runner for Ansible automation prep. It presents timed tasks, then verifies your work by SSHing into the Vagrant VMs and checking that everything was configured correctly.

## Quick Start

```bash
# From the rhce-study directory
pip install -r requirements.txt

# Start your Vagrant lab
cd Mac && vagrant up

# Launch the examiner
cd ..
python -m examiner
```

The TUI starts with a 4-hour countdown, 18 tasks in the sidebar, and the first task description loaded.

## How It Works

```
Your Mac (examiner TUI)          Vagrant VMs
┌──────────────────┐    SSH     ┌─────────────────┐
│  Task list       │───────────>│ control (.10)    │
│  Timer           │───────────>│ node1-5 (.20-24) │
│  Verify button   │            │ AlmaLinux 9      │
└──────────────────┘            └─────────────────┘
```

1. You read a task description in the TUI
2. You SSH into the control node (`vagrant ssh control`) and write/run your Ansible playbooks
3. You press `v` in the TUI to verify — it SSHes into the VMs and runs checks (file exists? service running? user created?)
4. Green = passed, red = failed, yellow = partial credit

## TUI Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Header                                                       │
├──────────────────┬───────────────────────────────────────────┤
│  TASKS sidebar   │  Status bar: title | timer | score        │
│  (scrollable)    │───────────────────────────────────────────│
│                  │  Task description                          │
│  OK 1. ansible   │                                           │
│  ~  2. repos     │  Verification Results:                    │
│     3. packages  │  OK  ansible.cfg exists                   │
│  X  4. timesync  │  X   inventory missing prod group         │
│     ...          │  OK  collections installed                 │
├──────────────────┴───────────────────────────────────────────┤
│  Footer: [v]Verify [V]Verify All [r]Reset [t]Timer [q]Quit   │
└──────────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `v` | Verify the currently selected task |
| `V` (shift+v) | Verify all tasks at once |
| `r` | Reset the current task results to pending |
| `R` (shift+r) | Reset all task results |
| `t` | Pause/resume the countdown timer |
| `c` | Test SSH connectivity to all VMs |
| `Up/Down` | Navigate between tasks |
| `q` | Quit |

## Status Icons

| Icon | Meaning |
|------|---------|
| (blank) | Not yet verified |
| `~` (yellow) | Partial — some checks pass, some fail |
| `OK` (green) | All checks pass |
| `X` (red) | All checks failed |

## Typical Workflow

1. **Start the lab:** `cd Mac && vagrant up`
2. **Launch the examiner:** `python -m examiner`
3. **Press `c`** to confirm all 6 VMs are reachable
4. **Read Task 1** in the right panel
5. **Open another terminal**, SSH into control: `cd Mac && vagrant ssh control`
6. **Do the work** — write playbooks, run them with `ansible-playbook`
7. **Press `v`** in the TUI to check your work
8. **Move to the next task** with arrow keys
9. **Repeat** until the timer runs out or all tasks are green
10. **Check your score** in the top-right — 70% to pass

## Timer

- The timer starts automatically when you launch the exam (4 hours for exam1)
- Press `t` to pause/resume (useful for breaks)
- Color changes: green (plenty of time) > yellow (< 1 hour) > red (< 30 min) > "TIME'S UP!"
- The timer is informational only — it won't lock you out when it expires

## Scoring

- Each task has a point value and multiple verification checks
- **Partial credit** is awarded: if a task has 8 checks and 6 pass, you earn 75% of that task's points
- Your total score percentage is shown in the top-right corner
- The passing threshold is displayed alongside your score

## Running a Specific Exam

```bash
# Auto-discovers the first exam in examiner/exams/
python -m examiner

# Run a specific exam file
python -m examiner examiner/exams/exam1.yml
python -m examiner examiner/exams/my_custom_exam.yml
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `EXAMINER_VAGRANT_DIR` | `rhce-study/Mac` | Path to the directory containing your Vagrantfile (used to find SSH keys) |

---

# Creating Your Own Exams and Courses

The examiner reads plain YAML files. You don't need to touch any Python code — just drop a `.yml` file into `examiner/exams/` (or anywhere, and pass the path as an argument).

## YAML Structure

```yaml
---
id: my-exam                    # Unique identifier
title: "My Custom Exam"        # Shown in the TUI header
duration: 7200                 # Time limit in seconds (7200 = 2 hours)
passing_score: 70              # Percentage needed to pass

# Define which VMs the checks will SSH into
hosts:
  control:
    hostname: control.lab.local
    ip: "192.168.56.10"
    ssh_user: vagrant
    groups: [control]
  node1:
    hostname: node1.lab.local
    ip: "192.168.56.20"
    ssh_user: vagrant
    groups: [workers]
  # ... add as many hosts as your lab has

# The tasks the student must complete
tasks:
  - id: "1"
    title: "Short Task Title"
    points: 5                  # How much this task is worth
    description: |
      Multi-line description of what the student should do.
      Be specific — include exact paths, package names, etc.

    checks:
      - id: "1.1"
        description: "Human-readable check description"
        node: control          # Which host to SSH into (must match a hosts key)
        command: "test -f /home/vagrant/ansible/playbook.yml"
        expect_rc: 0           # Expected exit code (0 = success)

      - id: "1.2"
        description: "Service is running"
        node: node1
        command: "systemctl is-active httpd"
        expect_stdout: "active"   # Exact stdout match (stripped)

      - id: "1.3"
        description: "Config contains the right setting"
        node: node1
        command: "cat /etc/myapp.conf"
        expect_stdout_contains: "max_connections=100"  # Substring match
```

## Check Types Reference

Every check runs a shell command on a VM via SSH. You control what "passing" means with three optional fields. All specified conditions must pass.

| Field | Type | Meaning |
|-------|------|---------|
| `expect_rc` | integer | Exit code must equal this (default: `0`) |
| `expect_stdout` | string | Stripped stdout must match exactly |
| `expect_stdout_contains` | string | Stdout must contain this substring |

### Common Check Patterns

```yaml
# File exists
- command: "test -f /path/to/file"
  expect_rc: 0

# File contains a line
- command: "grep -q 'some pattern' /path/to/file"
  expect_rc: 0

# File has specific permissions
- command: "stat -c '%a' /path/to/file"
  expect_stdout: "644"

# Package installed
- command: "rpm -q httpd"
  expect_rc: 0

# Service running
- command: "systemctl is-active httpd"
  expect_stdout: "active"

# Service enabled
- command: "systemctl is-enabled httpd"
  expect_stdout: "enabled"

# User exists
- command: "id username"
  expect_rc: 0

# User has specific shell
- command: "getent passwd username | cut -d: -f7"
  expect_stdout: "/bin/bash"

# Firewall rule
- command: "firewall-cmd --list-services | grep -q http"
  expect_rc: 0

# SELinux mode
- command: "getenforce"
  expect_stdout: "Enforcing"

# SELinux boolean
- command: "getsebool httpd_can_network_connect | grep -q 'on'"
  expect_rc: 0

# Cron job exists
- command: "crontab -l -u vagrant 2>/dev/null | grep -q 'pattern'"
  expect_rc: 0

# LVM logical volume exists
- command: "lvs --noheadings -o lv_name vg_name | grep -q 'lv_name'"
  expect_rc: 0

# Mount point active
- command: "findmnt /mnt/data"
  expect_rc: 0

# Ansible vault encrypted
- command: "head -1 /path/to/file"
  expect_stdout_contains: "$ANSIBLE_VAULT"

# Symlink target
- command: "readlink /path/to/link"
  expect_stdout: "/path/to/target"

# Directory exists
- command: "test -d /path/to/dir"
  expect_rc: 0

# Ansible playbook syntax check
- command: "cd /home/vagrant/ansible && ansible-playbook --syntax-check playbook.yml"
  expect_rc: 0
```

## Example: Creating a Second Exam

Save this as `examiner/exams/exam2.yml`:

```yaml
---
id: exam2
title: "Practice Exam 2 — Roles & Collections"
duration: 14400
passing_score: 70

hosts:
  control:
    hostname: control.lab.local
    ip: "192.168.56.10"
    ssh_user: vagrant
  node1:
    hostname: node1.lab.local
    ip: "192.168.56.20"
    ssh_user: vagrant
  node2:
    hostname: node2.lab.local
    ip: "192.168.56.21"
    ssh_user: vagrant

tasks:
  - id: "1"
    title: "Install ansible-core"
    points: 3
    description: |
      Ensure ansible-core is installed on the control node.
    checks:
      - id: "1.1"
        description: "ansible-core is installed"
        node: control
        command: "rpm -q ansible-core"
        expect_rc: 0

  # ... add more tasks
```

Then run it:

```bash
python -m examiner examiner/exams/exam2.yml
```

## Example: Mini-Course / Tutorial Mode

You can create shorter, focused scenarios that teach one concept at a time. Use a short timer (or a very long one if you don't want time pressure), fewer tasks, and detailed descriptions that guide the learner.

Save as `examiner/exams/lesson01_inventory.yml`:

```yaml
---
id: lesson01
title: "Lesson 1: Ansible Inventory Basics"
duration: 3600        # 1 hour — relaxed pace
passing_score: 100    # Must complete everything

hosts:
  control:
    hostname: control.lab.local
    ip: "192.168.56.10"
    ssh_user: vagrant
  node1:
    hostname: node1.lab.local
    ip: "192.168.56.20"
    ssh_user: vagrant
  node2:
    hostname: node2.lab.local
    ip: "192.168.56.21"
    ssh_user: vagrant

tasks:
  - id: "1"
    title: "Create a basic inventory file"
    points: 1
    description: |
      An Ansible inventory defines which hosts Ansible manages. The simplest
      format is an INI file with hostnames or IPs, one per line.

      Create the file /home/vagrant/ansible/inventory with this content:

        [webservers]
        node1.lab.local

        [dbservers]
        node2.lab.local

      Hint: use `vim` or `nano` on the control node.
    checks:
      - id: "1.1"
        description: "Inventory file exists"
        node: control
        command: "test -f /home/vagrant/ansible/inventory"
        expect_rc: 0
      - id: "1.2"
        description: "Inventory has [webservers] group"
        node: control
        command: "grep -q '\\[webservers\\]' /home/vagrant/ansible/inventory"
        expect_rc: 0
      - id: "1.3"
        description: "Inventory has [dbservers] group"
        node: control
        command: "grep -q '\\[dbservers\\]' /home/vagrant/ansible/inventory"
        expect_rc: 0

  - id: "2"
    title: "Test connectivity with ansible ping"
    points: 1
    description: |
      Now that you have an inventory, test that Ansible can reach your hosts.

      Run: ansible all -m ping -i /home/vagrant/ansible/inventory

      This uses the 'ping' module (not ICMP ping — it tests Ansible's SSH
      connectivity and Python availability on the remote host).

      If it fails, check:
      - Can you SSH manually? ssh vagrant@node1.lab.local
      - Is python3 installed on the nodes?
      - Does your ansible.cfg point to the right SSH key?

      The check below verifies that Ansible can reach node1.
    checks:
      - id: "2.1"
        description: "ansible ping reaches node1"
        node: control
        command: "ansible node1.lab.local -m ping -i /home/vagrant/ansible/inventory -u vagrant 2>/dev/null | grep -q SUCCESS"
        expect_rc: 0
      - id: "2.2"
        description: "ansible ping reaches node2"
        node: control
        command: "ansible node2.lab.local -m ping -i /home/vagrant/ansible/inventory -u vagrant 2>/dev/null | grep -q SUCCESS"
        expect_rc: 0

  - id: "3"
    title: "Add host variables to your inventory"
    points: 1
    description: |
      You can assign variables to hosts directly in the inventory. This is
      useful for setting per-host values like ports or custom paths.

      Update your inventory so node1 has a variable:

        [webservers]
        node1.lab.local http_port=8080

      Then verify it works:
        ansible node1.lab.local -m debug -a "var=http_port" -i inventory

      You should see: "http_port": "8080"
    checks:
      - id: "3.1"
        description: "node1 has http_port variable set"
        node: control
        command: "grep -q 'http_port' /home/vagrant/ansible/inventory"
        expect_rc: 0

  - id: "4"
    title: "Use group variables with [group:vars]"
    points: 1
    description: |
      Instead of setting variables per-host, you can set them for an entire
      group using [group:vars].

      Add this to your inventory:

        [all:vars]
        ansible_user=vagrant
        ansible_ssh_private_key_file=/home/vagrant/.ssh/id_rsa

      This tells Ansible to use the 'vagrant' user and the specified SSH key
      for every host in the inventory.
    checks:
      - id: "4.1"
        description: "Inventory has [all:vars] section"
        node: control
        command: "grep -q '\\[all:vars\\]' /home/vagrant/ansible/inventory"
        expect_rc: 0
      - id: "4.2"
        description: "ansible_user is set to vagrant"
        node: control
        command: "grep -q 'ansible_user=vagrant' /home/vagrant/ansible/inventory"
        expect_rc: 0
```

### Ideas for a Full Mini-Course

You could create a series of lesson files that build on each other:

```
examiner/exams/
├── exam1.yml                       # Full 4-hour practice exam
├── exam2.yml                       # Second practice exam (different tasks)
├── lesson01_inventory.yml          # Inventory basics
├── lesson02_adhoc.yml              # Ad-hoc commands
├── lesson03_first_playbook.yml     # Writing your first playbook
├── lesson04_variables_facts.yml    # Variables and facts
├── lesson05_handlers_templates.yml # Handlers and Jinja2 templates
├── lesson06_conditionals_loops.yml # when, loop, register
├── lesson07_roles.yml              # Creating and using roles
├── lesson08_vault.yml              # Ansible Vault
├── lesson09_system_roles.yml       # RHEL System Roles
└── lesson10_review.yml             # Comprehensive review
```

Each lesson: 3-5 tasks, ~30-60 min, with teaching built into the descriptions.

### Tips for Writing Good Scenarios

- **Descriptions teach.** Put hints, explanations, and example commands in the task description — that's where students spend their time reading.
- **Order tasks progressively.** Later tasks should build on earlier ones.
- **Use multiple checks per task.** Check both "did they create the file?" and "does the file have the right content?" — this gives partial credit and better feedback.
- **Test your checks.** Run the commands manually on the VM to make sure they work before adding them to the YAML.
- **Set `expect_rc: 0`** as the default — most checks are "did this command succeed?"
- **Use `expect_stdout_contains`** for flexible matching when exact output might vary (e.g., different whitespace).
