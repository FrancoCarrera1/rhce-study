# Getting Started — RHEL 9 + KVM/libvirt lab

Everything runs on one RHEL 9 machine, as root:

- **Vagrant** (via the `vagrant` podman wrapper in `/root/bin`) builds the VMs in KVM.
- **The examiner TUI** runs on the same machine and SSHes to the VMs on 192.168.56.x.
- You do the actual work inside the **control** VM.

```
RHEL 9 host (root)
├── terminal 1: examiner TUI  ──SSH──>  control (.10), node1-5 (.20-.24)
└── terminal 2: vagrant ssh control  →  write and run playbooks here
```

## 1. One-time setup

Repo layout this guide assumes:

```
~/rhce-study/
├── Vagrantfile          # the libvirt version
├── requirements.txt     # added (missing from the original repo)
└── ansible/
    ├── pyproject.toml   # fixed version
    └── examiner/        # the TUI package
```

Install the examiner's Python dependencies into a virtualenv:

```bash
cd ~/rhce-study
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

The original README's `pip install -r requirements.txt` failed because the file was never committed.
The venv keeps these packages out of the system Python that RHEL's own tools use.

## 2. Start the lab

```bash
cd ~/rhce-study
vagrant up --no-parallel
vagrant snapshot save clean-slate      # first time only
```

Check: `vagrant status` shows control and node1–node5 as `running`.

## 3. Run a lesson

The examiner **must be started from the `ansible/` folder**, since that's where the `examiner` package is.

**Terminal 1: examiner**

```bash
cd ~/rhce-study/ansible
source ../.venv/bin/activate
export EXAMINER_VAGRANT_DIR=~/rhce-study      # where .vagrant/ (the SSH keys) lives
python -m examiner examiner/exams/lesson01_configuration.yml
```

Press **`c`** first. All 6 VMs should show as connected.

**Terminal 2: do the work**

```bash
cd ~/rhce-study
vagrant ssh control
cd ~/ansible          # lessons use this folder (synced from the repo)
```

Back in the TUI, press **`v`** to verify the selected task, or **`V`** for all of them. Press **`q`** to quit.

Optional, so you don't retype the setup each time. Add to `/root/.bashrc`:

```bash
alias rhce='cd ~/rhce-study/ansible && source ../.venv/bin/activate && export EXAMINER_VAGRANT_DIR=~/rhce-study && python -m examiner'
```

Then run: `rhce examiner/exams/lesson02_getting_started.yml`

## 4. Lessons and exams

Files are in `ansible/examiner/exams/`. Lessons go in order **01 → 20**:

| File | Topic |
|---|---|
| `lesson01_configuration.yml` | ansible.cfg and inventory |
| `lesson02_getting_started.yml` | Lab check and ad-hoc commands |
| `lesson03_first_playbook.yml` | First playbook |
| … | … through `lesson20_webcontent_selinux.yml` |
| `exam1.yml`, `exam2.yml`, `exam3.yml`, `bonus_exam.yml` | 4-hour practice exams |

CURRICULUM.md says `lesson01_getting_started.yml`. That file doesn't exist; use the names above.

Lessons work in `/home/vagrant/ansible` on control, with Ansible pre-installed.
Exams work in `/home/vagrant/exam`, with Ansible **removed**, since installing it is part of Task 1.

## 5. Before each practice exam

```bash
cd ~/rhce-study
vagrant snapshot restore clean-slate
vagrant provision control --provision-with exam_reset
```

Then start the exam from terminal 1, for example `rhce examiner/exams/exam1.yml`.
After you finish, press **`e`** to export a grade report to `ansible/examiner/results/`.

## 6. Daily use

| Task | Command (run in `~/rhce-study`) |
|---|---|
| Start the VMs | `vagrant up --no-parallel` |
| Stop the VMs | `vagrant halt` |
| Reset everything | `vagrant snapshot restore clean-slate` |
| Get a fresh copy of the repo's `ansible/` on control | `vagrant provision control --provision-with copy_ansible,place_ansible` (lands in `~/ansible-refresh`) |
| Fewer VMs for early lessons | `NODES=3 vagrant up --no-parallel` |

`ansible/` is copied to control once, the first time it's built. After that, files you write on control stay on control. `vagrant up` and `halt` never overwrite them.

## Troubleshooting

- **`No module named examiner`**: you're not in `~/rhce-study/ansible`.
- **`No module named textual` / `yaml`**: the venv isn't active (`source ../.venv/bin/activate`).
- **`c` shows VMs unreachable**: check `vagrant status`, then `ping 192.168.56.20`. Also confirm `EXAMINER_VAGRANT_DIR` points at the folder that contains `.vagrant/`.
- **Exams that use node4/node5 fail**: you started with `NODES=3`. Run `vagrant up --no-parallel` without it.
