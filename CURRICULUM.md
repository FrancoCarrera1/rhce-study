# Ansible Automation Learning Curriculum

A structured learning path from Ansible beginner to assessment-ready, using the **examiner** TUI to verify your work at every step.

## How This Works

```
Lessons (learn)  ──>  Practice Exams (test)  ──>  Assessment

  20 lessons           3 full exams + bonus      4 hours, 17-22 tasks
  30-60 min each       4 hours each
  guided + tips        exam simulation
```

1. Work through the **20 lessons** in order. Each teaches one concept with hands-on tasks.
2. Take **Practice Exam 1** under timed conditions. Identify weak areas.
3. Review lessons for any topics you struggled with.
4. Take **Practice Exams 2 & 3** under timed conditions.
5. If scoring 70%+ consistently, you're ready for the final assessment.

**Key difference:** Lessons use the synced folder `/home/vagrant/ansible` with Ansible pre-installed. Exams use a separate directory `/home/vagrant/exam` with no Ansible pre-installed — installing it is part of Task 1.

## Running a Lesson or Exam

```bash
cd <project-root>

# Run a specific lesson
python -m examiner examiner/exams/lesson01_getting_started.yml

# Run practice exam 1
python -m examiner examiner/exams/exam1.yml

# Run practice exam 2
python -m examiner examiner/exams/exam2.yml
```

In the TUI: read the task, do the work on the control node (`vagrant ssh control`), press `v` to verify.

After an exam, press `e` to export a grade report to `examiner/results/`. Share it with Claude for detailed feedback on your playbooks.

---

## Learning Path

### Phase 1: Foundations (Lessons 01-04)

Get comfortable with Ansible basics. No prior Ansible experience needed.

| Lesson | Topic | Time | What You Learn |
|--------|-------|------|----------------|
| **01** | Getting Started & Ad-Hoc Commands | 30 min | What Ansible is, control/managed nodes, ping, ad-hoc commands |
| **02** | Ansible Configuration | 45 min | ansible.cfg, static inventory, groups, children, group_vars |
| **03** | Your First Playbook | 45 min | YAML structure, plays, tasks, dnf/copy/file modules, syntax-check |
| **04** | Managing Files & Packages | 45 min | copy, lineinfile, blockinfile, file permissions, package management |

**After Phase 1 you can:** Write simple playbooks, manage files and packages, understand inventory structure.

**Skills practiced:** ansible.cfg setup (Task 1 on every exam), inventory creation, basic modules.

### Phase 2: Core Skills (Lessons 05-08)

Master the building blocks used in every exam task.

| Lesson | Topic | Time | What You Learn |
|--------|-------|------|----------------|
| **05** | Variables & Facts | 45 min | vars, vars_files, ansible_facts, register, debug |
| **06** | Conditionals & Loops | 45 min | when: conditions, loop:, register with loops, group membership |
| **07** | Templates & Handlers | 60 min | Jinja2 templates (variables, for, if), handlers, notify |
| **08** | Users, Groups & Services | 45 min | user, group, service, firewalld, cron modules |

**After Phase 2 you can:** Write playbooks with variables, conditionals, loops, templates, handlers, and manage users/services.

**Skills practiced:** Jinja2 templates, conditional deployment by group, user creation with hashed passwords, service management, firewall rules.

### Phase 3: Advanced Topics (Lessons 09-12)

The topics that build on core Ansible skills.

| Lesson | Topic | Time | What You Learn |
|--------|-------|------|----------------|
| **09** | Roles | 60 min | Role structure, ansible-galaxy init, defaults/handlers/templates, Galaxy requirements.yml |
| **10** | Ansible Vault | 45 min | vault create/edit/view/rekey, vault password files, vault + playbooks |
| **11** | Collections & System Roles | 60 min | Installing collections, FQCNs, timesync role, selinux role |
| **12** | Readiness Review | 60 min | Timed drills combining all concepts: setup, multi-play, templates, roles, vault, error handling |

**After Phase 3 you can:** Create roles from scratch, encrypt sensitive data with Vault, use RHEL system roles, handle errors with block/rescue/always.

**Skills practiced:** Everything from Phase 1-2 plus roles, vault, collections, system roles.

### Phase 4: Advanced Skills (Lessons 13-17)

Deep-dive into patterns that require extra practice.

| Lesson | Topic | Time | What You Learn |
|--------|-------|------|----------------|
| **13** | Advanced Vault (encrypt_string, role deps) | 45 min | Inline vault, encrypting existing files, mixed vault/plain vars, role dependencies |
| **14** | Additional System Roles | 45 min | Discovering system roles, storage role (LVM), network role, firewall role |
| **15** | Jinja2 Templates & Loops | 60 min | The /etc/myhosts pattern, hostvars loop, conditionals in templates, default() filter |
| **16** | User Accounts with Vault | 60 min | vault password file, user_list.yml, password_hash('sha512'), when conditions with groups |
| **17** | LVM Storage & Error Handling | 60 min | block/rescue, ansible_lvm facts, lvol with fallback sizing, partition handling |

**After Phase 4 you can:** Handle advanced Ansible tasks including Jinja2 hosts file generation, vault-encrypted user creation, and LVM with error handling.

**Skills practiced:** Jinja2 template patterns, vault-encrypted user creation, LVM storage with error handling.

### Phase 5: Targeted Practice (Lessons 18-20)

Dedicated lessons for task types that benefit from extra drilling.

| Lesson | Topic | Time | What You Learn |
|--------|-------|------|----------------|
| **18** | YUM Repositories | 45 min | yum_repository module, BaseOS/AppStream repos, GPG keys, package verification |
| **19** | Galaxy Roles & Requirements | 60 min | requirements.yml with src+name, ansible-galaxy install, mixing Galaxy + custom roles |
| **20** | Web Content & SELinux | 60 min | Setgid directories, sefcontext + restorecon, symlinks, SELinux booleans |

**After Phase 5 you can:** Confidently handle the repo, Galaxy, and web content/SELinux tasks.

**Skills practiced:** yum_repository module, Galaxy role requirements files, SELinux file contexts, setgid permissions.

---

## Practice Exams

After completing all 20 lessons, test yourself under timed conditions.

**Exam mode differences from lessons:**
- Exams use `/home/vagrant/exam` (non-synced, clean directory) instead of `/home/vagrant/ansible`
- Ansible is NOT pre-installed — installing it is part of Task 1
- Each exam includes reference solutions in the grade report (press `e` after grading)
- Host group assignments vary between exams to test adaptability

### Practice Exam 1 — Full Assessment Template
- **17 tasks**, 76 checks, 300 total points, **70% to pass (210 pts)**
- Groups: dev (node1), test (node2), prod/webservers (node3, node4), balancers (node5)
- Covers: ansible.cfg, inventory, repos, collections, Galaxy roles, apache role, roles.yml, packages, timesync, web content, hardware report, /etc/issue, hosts.j2 template, vault, users with vault, rekey, cron, LVM
- **Target time:** 4 hours

### Practice Exam 2 — Full Assessment Template (Variant)
- **18 tasks**, 112 checks, 301 total points, **70% to pass (211 pts)**
- Same pattern as Exam 1 with different specific values
- Groups: dev (node1), test (node2), prod/webservers (node3), balancers (node4)
- Covers: ansible.cfg, repos, collections, Galaxy roles, custom role, multi-role playbooks, system roles (timesync + selinux), packages, web content, hardware report, /etc/issue, hosts.j2 template, vault, users, rekey, cron, LVM
- **Target time:** 4 hours

### Practice Exam 3 — Mock Assessment
- **10 tasks**, 68 checks, 300 total points, **70% to pass (210 pts)**
- Groups: workers/webservers/dbservers/lab (5 nodes — different structure)
- Covers: ansible.cfg, ad-hoc scripts, vault users, packages/services, Jinja2 templates, custom roles, system roles, firewall/SELinux, conditionals/loops, error handling
- **Target time:** 4 hours

### Bonus Exam — Topic Review
- **18 tasks**, 103 checks, 300 total points, **70% to pass (210 pts)**
- Broader topic coverage
- Groups: webservers (node1-2), dbservers (node3-4), balancers (node5), lab:children (all)
- Covers: ansible.cfg, repos, packages, timesync, vault, users, SSH banner template, Apache, /etc/hosts, cron, LVM, SELinux, roles, Galaxy, conditionals, lineinfile, custom facts, system report
- **Target time:** 4 hours

### How to Take a Practice Exam

1. **Reset your lab** to a clean state:
   ```bash
   cd Mac && vagrant snapshot restore clean-slate
   ```
   (Or `vagrant destroy -f && vagrant up` if no snapshot exists)

2. **Remove Ansible and prepare the exam directory:**
   ```bash
`   vagrant provision control --provision-with exam_reset
   ```
   This removes `ansible-core`, `ansible-navigator`, and `pip`, then creates an empty `/home/vagrant/exam` directory. Installing Ansible is part of Task 1.

3. **Close all reference materials.** During timed practice you should rely only on `ansible-doc` and local system docs.

4. **Start the exam:**
   ```bash
   python -m examiner examiner/exams/exam1.yml
   ```

5. **Work through tasks** in order (or skip and come back). All work goes in `/home/vagrant/exam`.

6. **Press `V`** (Verify All) when done to see your final score.

7. **Press `e`** to export a grade report with your scores, playbook contents, and **reference solutions**.

8. **70% to pass.** Review any failed checks and compare with the solutions.

---

## Skill Area Mapping

Every skill area is covered by at least one lesson and one practice exam task.

| Skill Area | Lessons | Exam Tasks |
|----------------|---------|------------|
| **Install and configure Ansible** | 01, 02 | E1-1, E2-1, E3-1 |
| **Create static inventories** | 02 | E1-1, E2-1 |
| **Manage Ansible config files** | 02 | E1-1, E2-1 |
| **Use Ansible Vault** | 10, 13, 16 | E1-13/15, E2-13/14/15 |
| **Run playbooks** | 03, 04 | All exams |
| **Commonly used modules** | 03, 04, 08 | All exams |
| **Variables, register, debug** | 05 | E1-10/12, E2-10/12 |
| **Conditionals (when)** | 06, 16 | E1-11/14, E2-11/14 |
| **Loops** | 06, 16 | E1-14, E2-14 |
| **Error handling (block/rescue)** | 12, 17 | E1-17, E2-17 |
| **Jinja2 templates** | 07, 15 | E1-10/12, E2-10/12 |
| **Handlers** | 07 | E1-5, E2-5 |
| **Manage packages & repos** | 04, 18 | E1-2/7, E2-2/8 |
| **Manage services** | 08 | E1-5/6, E2-5/6 |
| **Manage firewall** | 08 | E1-5/9, E2-5/9 |
| **Manage file content** | 04, 07 | E1-11, E2-11 |
| **Schedule cron jobs** | 08 | E1-16, E2-16 |
| **Manage users & groups** | 08, 16 | E1-14, E2-14 |
| **Manage SELinux** | 11, 20 | E1-9, E2-9 |
| **Manage storage (LVM)** | 14, 17 | E1-17, E2-17 |
| **Create & use roles** | 09 | E1-5/6, E2-5/6 |
| **Install roles from Galaxy** | 09, 19 | E1-4, E2-4 |
| **Install & use collections** | 11 | E1-3, E2-3 |
| **RHEL system roles (timesync)** | 11 | E1-8, E2-7a |
| **RHEL system roles (selinux)** | 11, 14 | E2-7b |
| **Custom facts** | 05 | Bonus-17 |

---

## Study Tips

### Before You Start

- Set up your Vagrant lab: `cd Mac && vagrant up`
- Take a snapshot of the clean state: `vagrant snapshot save clean-slate`
- Restore anytime: `vagrant snapshot restore clean-slate`

### During Lessons

- **Type everything yourself.** Don't copy-paste. Muscle memory matters under timed conditions.
- **Use `ansible-doc`** to look up every module you encounter:
  ```bash
  ansible-doc ansible.builtin.copy
  ansible-doc ansible.posix.firewalld
  ansible-doc -l | grep firewall
  ```
- **Always syntax-check** before running:
  ```bash
  ansible-playbook --syntax-check playbook.yml
  ```
- **Use `--check --diff`** for dry runs:
  ```bash
  ansible-playbook playbook.yml --check --diff
  ```
- **Use FQCNs** (ansible.builtin.copy, not just copy). This is mandatory for collection-based modules.

### During Practice Exams

- **Read ALL tasks first** before starting — some build on each other.
- **Do the easy tasks first** (ansible.cfg, inventory, vault password file).
- **Budget 12-15 minutes per task.** Skip and come back if stuck for >10 min.
- **Save 15 minutes at the end** to run all playbooks one final time.
- **Partial credit exists** — if you can't finish a task, complete what you can.

### Common Mistakes

1. **YAML indentation** — 2 spaces, never tabs. The #1 cause of failures.
2. **Forgetting `become`** — Most tasks need root. Set it in ansible.cfg.
3. **Not installing collections** — firewalld, sefcontext, parted are NOT in ansible-core.
4. **Vault password** — Always have a `vault_password_file` in ansible.cfg.
5. **System role variable names** — Check docs, don't guess. The variable names are specific.

### Quick Reference

```bash
# Core commands
ansible all -m ping                              # Test connectivity
ansible-playbook --syntax-check playbook.yml     # Syntax check
ansible-playbook playbook.yml --check --diff     # Dry run
ansible-doc ansible.builtin.copy                 # Module docs

# Vault
ansible-vault create secret.yml --vault-password-file=pass.txt
ansible-vault view secret.yml --vault-password-file=pass.txt
ansible-vault rekey secret.yml

# Galaxy
ansible-galaxy init roles/myrole                 # Create role skeleton
ansible-galaxy install -r roles/requirements.yml -p roles/
ansible-galaxy collection install ansible.posix -p collections/

# Troubleshooting
ansible-playbook playbook.yml -vvv               # Verbose output
ansible <host> -m setup | grep <fact>            # Find facts
ansible-config dump --only-changed               # Check config
```

---

## File Listing

```
examiner/exams/
├── lesson01_configuration.yml            # Phase 1: Foundations
├── lesson02_getting_started.yml
├── lesson03_first_playbook.yml
├── lesson04_files_and_packages.yml
├── lesson05_variables_and_facts.yml      # Phase 2: Core Skills
├── lesson06_conditionals_and_loops.yml
├── lesson07_templates_and_handlers.yml
├── lesson08_users_groups_services.yml
├── lesson09_roles.yml                    # Phase 3: Advanced
├── lesson10_vault.yml
├── lesson11_collections_and_system_roles.yml
├── lesson12_exam_readiness.yml
├── lesson13_advanced_vault.yml           # Phase 4: Advanced Skills
├── lesson14_additional_system_roles.yml
├── lesson15_jinja2_templates.yml
├── lesson16_user_accounts.yml
├── lesson17_lvm_storage.yml
├── lesson18_repos_and_yum.yml            # Phase 5: Targeted Practice
├── lesson19_galaxy_roles.yml
├── lesson20_webcontent_selinux.yml
├── exam1.yml                             # Practice Exams (use /home/vagrant/exam)
├── exam2.yml
├── exam3.yml
└── bonus_exam.yml

examiner/solutions/                        # Reference solutions (included in grade reports)
├── exam1_solutions.md
├── exam2_solutions.md
├── exam3_solutions.md
└── bonus_exam_solutions.md
```

Run any of them with:
```bash
cd <project-root>
python -m examiner examiner/exams/<filename>.yml
```
