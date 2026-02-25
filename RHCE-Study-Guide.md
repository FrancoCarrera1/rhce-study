# RHCE EX294 Study Guide

> Red Hat Certified Engineer — Ansible Automation on RHEL 9
> Last updated: February 2026

---

## Table of Contents

- [[#1. Exam Overview]]
- [[#2. Exam Objectives (RHEL 9 / V9)]]
- [[#3. V8 vs V9 Key Differences]]
- [[#4. 8-Week Study Plan]]
- [[#5. Practice Lab Exercises]]
- [[#6. Mock Exam]]
- [[#7. Exam Tips from Test Takers]]
- [[#8. Essential Commands Quick Reference]]
- [[#9. Recommended Resources]]

---

## 1. Exam Overview

| Detail | Info |
|---|---|
| **Exam Code** | EX294 |
| **Full Name** | Red Hat Certified Engineer (RHCE) exam for RHEL 9 |
| **Duration** | 4 hours |
| **Format** | Performance-based (hands-on, no multiple choice) |
| **Passing Score** | 210 / 300 (70%) |
| **Number of Tasks** | ~17–22 tasks |
| **Prerequisite** | Valid RHCSA (EX200) certification |
| **Cost** | ~$500 USD |
| **Delivery** | Remote (home) or Red Hat testing center |
| **RHEL Version** | RHEL 9 (V9 exam variant) |
| **Ansible Version** | ansible-core 2.14+ with Automation Platform 2.x |

### What the Exam Tests

You must demonstrate the ability to **write Ansible playbooks** to configure and manage RHEL 9 systems. Everything is hands-on — you are given a control node and several managed hosts and must complete tasks against a time limit. There is no internet access during the exam.

### Exam Environment

- 1 control node + multiple managed nodes (typically 4–5)
- RHEL 9 systems
- `ansible-navigator` is the primary tool (V9 change)
- `ansible-doc` and `ansible-navigator doc` are available for module documentation
- Man pages and local system documentation that ships with RHEL
- Web-based console (not your own terminal) — copy-paste may behave differently than expected
- No external internet access — practice without internet!

---

## 2. Exam Objectives (RHEL 9 / V9)

These are the **official objectives** from Red Hat's EX294 exam page.

### 2.1 Understand and Use Essential Ansible Components

- Manage Ansible configuration files
- Create and manage inventories (static)
- Manage parallelism with forks and serial
- Use Ansible Vault for encryption

### 2.2 Install and Configure an Ansible Control Node

- Install required packages (`ansible-core`, `ansible-navigator`)
- Create a configuration file to connect to managed hosts
- Create and use static inventories to define groups and hosts
- Manage parallelism

### 2.3 Configure Ansible Managed Nodes

- Create and distribute SSH keys to managed nodes
- Configure privilege escalation on managed nodes
- Deploy files to managed nodes
- Be able to analyze simple shell scripts and convert them to playbooks

### 2.4 Run Playbooks with Automation Content Navigator

- Use `ansible-navigator` to run playbooks
- Find new modules in available content collections using documentation
- Use `ansible-navigator` to check playbook syntax and run in check mode

### 2.5 Create Ansible Plays and Playbooks

- Know how to work with commonly used Ansible modules:
  - **Files:** `ansible.builtin.copy`, `ansible.builtin.file`, `ansible.builtin.template`, `ansible.builtin.lineinfile`, `ansible.builtin.replace`
  - **Packages:** `ansible.builtin.dnf`, `ansible.builtin.package`
  - **Services:** `ansible.builtin.service`, `ansible.builtin.systemd`
  - **Users/Groups:** `ansible.builtin.user`, `ansible.builtin.group`
  - **Firewall:** `ansible.posix.firewalld`
  - **SELinux:** `ansible.posix.seboolean`, `community.general.sefcontext`
  - **Storage:** `community.general.parted`, `community.general.lvg`, `community.general.lvol`, `ansible.builtin.mount`
  - **System:** `ansible.builtin.cron`, `ansible.builtin.hostname`, `ansible.builtin.reboot`
  - **Commands:** `ansible.builtin.command`, `ansible.builtin.shell`, `ansible.builtin.raw`
  - **Network:** `ansible.builtin.get_url`, `ansible.builtin.uri`
- Use variables to retrieve the results of running a command (`register`)
- Use conditionals to control play execution (`when`)
- Configure error handling (`block`, `rescue`, `always`, `ignore_errors`)
- Create playbooks to configure systems to a specified state

### 2.6 Automate Standard RHCSA Tasks Using Ansible

- Manage software packages and repositories
- Manage services
- Manage firewall rules
- Manage file content and templates
- Schedule tasks using cron
- Manage users and groups
- Manage storage (LVM, partitions, file systems, mounts)
- Manage SELinux settings

### 2.7 Use Roles and Ansible Content Collections

- Create and work with roles
- Install roles and use them in playbooks
- Install content collections and use them in playbooks
- Obtain a set of related roles and supplementary modules from content collections

### 2.8 Use Advanced Ansible Features

- Create and use templates to create customized configuration files (Jinja2)
- Use Ansible Vault in playbooks to protect sensitive data
- Use provided RHEL system roles:
  - `rhel-system-roles.timesync`
  - `rhel-system-roles.selinux`
  - `rhel-system-roles.network`
  - `rhel-system-roles.firewall`
  - `rhel-system-roles.storage`

### 2.9 Manage Inventories

- Create static inventory files
- Manage inventory variables (host_vars, group_vars)
- Use patterns to target specific hosts and groups
- Connect to managed hosts using inventory groups

---

## 3. V8 vs V9 Key Differences

> If you studied with V8 materials, pay attention to these changes.

| Area | V8 (RHEL 8) | V9 (RHEL 9) |
|---|---|---|
| **Primary tool** | `ansible-playbook` | `ansible-navigator` |
| **Ansible version** | ansible 2.9 (full package) | ansible-core 2.14+ (minimal) |
| **Module names** | Short names (`copy`, `yum`) | FQCNs required (`ansible.builtin.copy`, `ansible.builtin.dnf`) |
| **Collections** | All modules bundled | Must install collections separately |
| **Package manager module** | `yum` | `dnf` (though `yum` still works as alias) |
| **System roles package** | `rhel-system-roles` | `rhel-system-roles` (same name, but role paths may differ) |
| **Execution environments** | N/A | Container-based EEs via `ansible-navigator` |
| **Documentation** | `ansible-doc` | `ansible-navigator doc` (or `ansible-doc`) |

### Critical V9 Gotchas

1. **FQCN is mandatory** — `ansible.builtin.copy` not just `copy`. Short names may work but FQCNs are the safe bet on the exam.

2. **ansible-navigator replaces ansible-playbook** — Learn `ansible-navigator run` syntax:
   ```bash
   ansible-navigator run playbook.yml -m stdout
   ```
   The `-m stdout` flag gives you familiar terminal output (instead of the TUI).

3. **Collections must be installed** — Modules like `firewalld`, `parted`, `sefcontext` are NOT in `ansible-core`. You need:
   ```bash
   ansible-galaxy collection install ansible.posix
   ansible-galaxy collection install community.general
   ```
   Or define them in `collections/requirements.yml`.

4. **rhel-system-roles** — Install via `dnf install rhel-system-roles`. The roles are at `/usr/share/ansible/roles/` and collections at `/usr/share/ansible/collections/`. On V9, you can reference them either as:
   - Role: `rhel-system-roles.timesync`
   - FQCN: `redhat.rhel_system_roles.timesync`

   > **V9 Gotcha:** RPM-installed `rhel-system-roles` are NOT visible inside the ansible-navigator execution environment. On the exam, the collection may be provided as a tarball to install via `ansible-galaxy collection install`. If using `--ee false`, the RPM-installed roles work fine.

5. **ansible-navigator default user** — When running inside an EE, the default user is `root`, not your current user. This can cause issues with SSH keys and privilege escalation. Always set `remote_user` explicitly in `ansible.cfg` or your plays.

6. **ansible-navigator settings** — Create `ansible-navigator.yml` in your project directory:
   ```yaml
   ---
   ansible-navigator:
     execution-environment:
       enabled: false
     mode: stdout
     playbook-artifact:
       enable: false
   ```
   This disables the EE container and gives you stdout mode (simpler for the exam).

---

## 4. 8-Week Study Plan

### Week 1: Foundations & Environment Setup

- [ ] Set up your Vagrant lab (`vagrant up` from this repo)
- [ ] Install and configure `ansible-core` and `ansible-navigator`
- [ ] Create `ansible.cfg` with inventory, remote_user, privilege escalation
- [ ] Create static inventory with groups (`[webservers]`, `[dbservers]`, `[all]`)
- [ ] Verify connectivity: `ansible all -m ping`
- [ ] Practice ad-hoc commands: `ansible all -m command -a "hostname"`
- [ ] Read: Official EX294 objectives

### Week 2: Playbook Basics

- [ ] Write playbooks using `copy`, `file`, `template`, `lineinfile`
- [ ] Work with variables: `vars`, `vars_files`, `host_vars`, `group_vars`
- [ ] Use `register` and `debug` to capture and display output
- [ ] Conditionals with `when`
- [ ] Loops with `loop` and `with_items`
- [ ] Handlers and `notify` / `listen`
- [ ] Practice: Labs 1–8

### Week 3: Users, Packages, Services

- [ ] Manage users and groups with `user` and `group` modules
- [ ] Manage packages with `dnf` module
- [ ] Manage services with `service` / `systemd` modules
- [ ] Manage cron jobs with `cron` module
- [ ] Practice file content management with `lineinfile`, `blockinfile`
- [ ] Practice: Labs 9–14

### Week 4: Roles & Galaxy

- [ ] Create custom roles using `ansible-galaxy init`
- [ ] Understand role directory structure: `tasks/`, `handlers/`, `templates/`, `vars/`, `defaults/`, `meta/`
- [ ] Install roles from Galaxy: `ansible-galaxy install geerlingguy.apache`
- [ ] Use `requirements.yml` for role dependencies
- [ ] Install and use content collections
- [ ] Practice: Labs 15–18

### Week 5: Ansible Vault & Security

- [ ] Create encrypted files: `ansible-vault create`, `edit`, `view`
- [ ] Encrypt variables: `ansible-vault encrypt_string`
- [ ] Use vault passwords in playbooks: `--vault-password-file`
- [ ] Manage SELinux with `seboolean`, `sefcontext`, `restorecon`
- [ ] Manage firewall rules with `firewalld` module
- [ ] Practice: Labs 19–22

### Week 6: RHEL System Roles & Advanced Features

- [ ] Install `rhel-system-roles` package
- [ ] Configure NTP with `rhel-system-roles.timesync`
- [ ] Configure networking with `rhel-system-roles.network`
- [ ] Configure storage with `rhel-system-roles.storage`
- [ ] Configure firewall with `rhel-system-roles.firewall`
- [ ] Configure SELinux with `rhel-system-roles.selinux`
- [ ] Use Jinja2 templates with `for` loops and `if` conditionals
- [ ] Error handling: `block`, `rescue`, `always`
- [ ] Practice: Labs 23–29

### Week 7: Mock Exams & Review

- [ ] Complete Mock Exam (Section 6) under timed conditions (3 hours)
- [ ] Review any weak areas identified
- [ ] Redo failed practice labs from weeks 1–6
- [ ] Practice with Lisenet sample exam
- [ ] Practice with RedHatRanger RHCE9Vagrant scenarios
- [ ] Time yourself on each task (aim for 10–15 min per task)

### Week 8: Final Review & Exam Prep

- [ ] Speed run: complete 10 random labs in under 2.5 hours
- [ ] Review the Quick Reference (Section 8)
- [ ] Re-read exam tips (Section 7)
- [ ] Verify you can set up `ansible.cfg`, inventory, and vault from scratch without notes
- [ ] Ensure you can write a role from scratch in under 15 minutes
- [ ] Rest the day before the exam

---

## 5. Practice Lab Exercises

> **Lab Environment:** 1 control node (`control`) + 3 managed nodes (`node1`, `node2`, `node3`)
> All AlmaLinux 9 / RHEL 9. Network: `192.168.56.0/24`

---

### Lab 1: Configure ansible.cfg

**Objective:** 2.1, 2.2 — Install and configure Ansible control node

**Task:** Create `/home/vagrant/ansible/ansible.cfg` with:
- Inventory file: `/home/vagrant/ansible/inventory`
- Remote user: `vagrant`
- Privilege escalation enabled (become)
- Become method: `sudo`
- Host key checking disabled
- Forks: 5

**Solution:**

```ini
[defaults]
inventory = /home/vagrant/ansible/inventory
remote_user = vagrant
host_key_checking = False
forks = 5

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
```

**Verification:**

```bash
ansible --version        # Confirm config file path
ansible all -m ping      # Confirm connectivity
```

---

### Lab 2: Create Static Inventory

**Objective:** 2.2, 2.9 — Create and manage static inventories

**Task:** Create `/home/vagrant/ansible/inventory` with:
- `node1` in group `webservers`
- `node2` in group `dbservers`
- `node3` in group `webservers` and `dbservers`
- A parent group `lab` containing `webservers` and `dbservers`

**Solution:**

```ini
[webservers]
node1.lab.local
node3.lab.local

[dbservers]
node2.lab.local
node3.lab.local

[lab:children]
webservers
dbservers
```

**Verification:**

```bash
ansible-navigator inventory -m stdout --list
ansible-navigator inventory -m stdout --graph
ansible webservers --list-hosts
ansible dbservers --list-hosts
ansible lab --list-hosts
```

---

### Lab 3: Ad-Hoc Commands

**Objective:** 2.3 — Configure managed nodes, run ad-hoc commands

**Task:** Using ad-hoc commands only (no playbooks):
1. Verify all nodes are reachable
2. Check the OS version on all nodes
3. Create the directory `/opt/ansible-test` on all webservers
4. Copy `/etc/hostname` from control to `/tmp/control-hostname` on all nodes
5. Install `httpd` on webservers

**Solution:**

```bash
# 1. Ping all
ansible all -m ping

# 2. OS version
ansible all -m command -a "cat /etc/redhat-release"

# 3. Create directory on webservers
ansible webservers -m file -a "path=/opt/ansible-test state=directory mode=0755"

# 4. Copy file
ansible all -m copy -a "src=/etc/hostname dest=/tmp/control-hostname"

# 5. Install httpd
ansible webservers -m dnf -a "name=httpd state=present"
```

**Verification:**

```bash
ansible webservers -m command -a "ls -ld /opt/ansible-test"
ansible all -m command -a "cat /tmp/control-hostname"
ansible webservers -m command -a "rpm -q httpd"
```

---

### Lab 4: First Playbook — Package & Service Management

**Objective:** 2.5, 2.6 — Create playbooks, manage packages and services

**Task:** Write `web-setup.yml` that:
1. Installs `httpd` and `mod_ssl` on webservers
2. Starts and enables `httpd`
3. Opens ports 80 and 443 in the firewall
4. Creates `/var/www/html/index.html` with content "Hello from {{ inventory_hostname }}"

**Solution:**

```yaml
---
- name: Configure web servers
  hosts: webservers
  tasks:
    - name: Install web packages
      ansible.builtin.dnf:
        name:
          - httpd
          - mod_ssl
        state: present

    - name: Start and enable httpd
      ansible.builtin.service:
        name: httpd
        state: started
        enabled: true

    - name: Open firewall ports
      ansible.posix.firewalld:
        service: "{{ item }}"
        permanent: true
        immediate: true
        state: enabled
      loop:
        - http
        - https

    - name: Create index page
      ansible.builtin.copy:
        content: "Hello from {{ inventory_hostname }}\n"
        dest: /var/www/html/index.html
        owner: apache
        group: apache
        mode: '0644'
```

**Verification:**

```bash
ansible-navigator run web-setup.yml -m stdout
ansible webservers -m uri -a "url=http://localhost return_content=yes"
ansible webservers -m command -a "firewall-cmd --list-services"
```

---

### Lab 5: Variables and Facts

**Objective:** 2.5 — Use variables, register, facts

**Task:** Write `system-info.yml` that:
1. Gathers facts on all hosts
2. Creates `/etc/motd` using a variable for the company name
3. Displays: hostname, IP address, total memory, OS family
4. Creates `/root/system-info.txt` with the above information

**Solution:**

```yaml
---
- name: Gather and display system info
  hosts: all
  vars:
    company_name: "RHCE Lab Inc."
  tasks:
    - name: Set MOTD
      ansible.builtin.copy:
        content: "Welcome to {{ company_name }} — {{ inventory_hostname }}\n"
        dest: /etc/motd

    - name: Display system facts
      ansible.builtin.debug:
        msg: >
          Hostname: {{ ansible_fqdn }},
          IP: {{ ansible_default_ipv4.address }},
          Memory: {{ ansible_memtotal_mb }} MB,
          OS: {{ ansible_os_family }}

    - name: Save system info to file
      ansible.builtin.copy:
        content: |
          Hostname: {{ ansible_fqdn }}
          IP Address: {{ ansible_default_ipv4.address }}
          Total Memory: {{ ansible_memtotal_mb }} MB
          OS Family: {{ ansible_os_family }}
          Kernel: {{ ansible_kernel }}
        dest: /root/system-info.txt
        mode: '0644'
```

**Verification:**

```bash
ansible-navigator run system-info.yml -m stdout
ansible all -m command -a "cat /etc/motd"
ansible all -m command -a "cat /root/system-info.txt"
```

---

### Lab 6: Conditionals

**Objective:** 2.5 — Use conditionals to control play execution

**Task:** Write `conditional-packages.yml` that:
1. Installs `httpd` only on webservers (using group membership)
2. Installs `mariadb-server` only on dbservers
3. Installs `chrony` on all hosts but only if it is not already installed
4. Restarts `chronyd` only when the OS major version is 9

**Solution:**

```yaml
---
- name: Conditional package installation
  hosts: all
  tasks:
    - name: Install httpd on webservers
      ansible.builtin.dnf:
        name: httpd
        state: present
      when: "'webservers' in group_names"

    - name: Install mariadb-server on dbservers
      ansible.builtin.dnf:
        name: mariadb-server
        state: present
      when: "'dbservers' in group_names"

    - name: Check if chrony is installed
      ansible.builtin.command: rpm -q chrony
      register: chrony_check
      ignore_errors: true
      changed_when: false

    - name: Install chrony if missing
      ansible.builtin.dnf:
        name: chrony
        state: present
      when: chrony_check.rc != 0

    - name: Restart chronyd on RHEL 9
      ansible.builtin.service:
        name: chronyd
        state: restarted
      when: ansible_distribution_major_version == "9"
```

**Verification:**

```bash
ansible-navigator run conditional-packages.yml -m stdout
ansible webservers -m command -a "rpm -q httpd"
ansible dbservers -m command -a "rpm -q mariadb-server"
```

---

### Lab 7: Loops

**Objective:** 2.5 — Use loops in playbooks

**Task:** Write `create-users-loop.yml` that:
1. Creates users `alice`, `bob`, `charlie` on all hosts with specific UIDs
2. Creates directories `/opt/app1`, `/opt/app2`, `/opt/app3` with specific permissions
3. Installs multiple packages using a loop

**Solution:**

```yaml
---
- name: Loop examples
  hosts: all
  vars:
    users:
      - name: alice
        uid: 2001
      - name: bob
        uid: 2002
      - name: charlie
        uid: 2003
    app_dirs:
      - path: /opt/app1
        mode: '0755'
      - path: /opt/app2
        mode: '0750'
      - path: /opt/app3
        mode: '0700'
    packages:
      - tree
      - wget
      - vim-enhanced
  tasks:
    - name: Create users
      ansible.builtin.user:
        name: "{{ item.name }}"
        uid: "{{ item.uid }}"
        state: present
      loop: "{{ users }}"

    - name: Create app directories
      ansible.builtin.file:
        path: "{{ item.path }}"
        state: directory
        mode: "{{ item.mode }}"
      loop: "{{ app_dirs }}"

    - name: Install packages
      ansible.builtin.dnf:
        name: "{{ packages }}"
        state: present
```

**Verification:**

```bash
ansible-navigator run create-users-loop.yml -m stdout
ansible all -m command -a "id alice"
ansible all -m command -a "id bob"
ansible all -m command -a "ls -ld /opt/app1 /opt/app2 /opt/app3"
```

---

### Lab 8: Handlers

**Objective:** 2.5 — Use handlers for triggered actions

**Task:** Write `apache-config.yml` that:
1. Installs `httpd` on webservers
2. Deploys a custom `httpd.conf` (use template or copy)
3. Uses a handler to restart `httpd` only when the config changes
4. Opens the firewall for HTTP

**Solution:**

```yaml
---
- name: Configure Apache with handlers
  hosts: webservers
  tasks:
    - name: Install httpd
      ansible.builtin.dnf:
        name: httpd
        state: present

    - name: Deploy httpd config
      ansible.builtin.lineinfile:
        path: /etc/httpd/conf/httpd.conf
        regexp: '^ServerAdmin'
        line: 'ServerAdmin admin@lab.local'
      notify: Restart httpd

    - name: Ensure httpd is started and enabled
      ansible.builtin.service:
        name: httpd
        state: started
        enabled: true

    - name: Open firewall for http
      ansible.posix.firewalld:
        service: http
        permanent: true
        immediate: true
        state: enabled

  handlers:
    - name: Restart httpd
      ansible.builtin.service:
        name: httpd
        state: restarted
```

**Verification:**

```bash
ansible-navigator run apache-config.yml -m stdout
# Run again — handler should NOT fire (no changes)
ansible-navigator run apache-config.yml -m stdout
ansible webservers -m command -a "grep ServerAdmin /etc/httpd/conf/httpd.conf"
```

---

### Lab 9: Managing Users and Groups

**Objective:** 2.6 — Manage users and groups

**Task:** Write `user-management.yml` that:
1. Creates group `developers` with GID 3000
2. Creates group `admins` with GID 3001
3. Creates user `devuser1` in `developers` group with a password (vault-encrypted)
4. Creates user `devuser2` in `developers` group
5. Creates user `adminuser1` in `admins` group with sudo access
6. Sets SSH authorized keys for `adminuser1`

**Solution:**

```yaml
---
- name: Manage users and groups
  hosts: all
  vars:
    dev_password: "{{ 'redhat123' | password_hash('sha512', 'salt') }}"
  tasks:
    - name: Create developers group
      ansible.builtin.group:
        name: developers
        gid: 3000
        state: present

    - name: Create admins group
      ansible.builtin.group:
        name: admins
        gid: 3001
        state: present

    - name: Create devuser1
      ansible.builtin.user:
        name: devuser1
        uid: 3001
        group: developers
        password: "{{ dev_password }}"
        state: present

    - name: Create devuser2
      ansible.builtin.user:
        name: devuser2
        uid: 3002
        group: developers
        state: present

    - name: Create adminuser1
      ansible.builtin.user:
        name: adminuser1
        uid: 3003
        group: admins
        state: present

    - name: Grant sudo to adminuser1
      ansible.builtin.copy:
        content: "adminuser1 ALL=(ALL) NOPASSWD: ALL\n"
        dest: /etc/sudoers.d/adminuser1
        mode: '0440'
        validate: '/usr/sbin/visudo -cf %s'
```

**Verification:**

```bash
ansible-navigator run user-management.yml -m stdout
ansible all -m command -a "getent group developers"
ansible all -m command -a "getent group admins"
ansible all -m command -a "id devuser1"
ansible all -m command -a "id adminuser1"
ansible all -m command -a "cat /etc/sudoers.d/adminuser1"
```

---

### Lab 10: Managing Users from a Variable File

**Objective:** 2.5, 2.6 — Variables and user management

**Task:** Create a `vars/users.yml` file containing a list of users with properties (name, groups, password hash). Write `users-from-vars.yml` that reads this file and creates all users with their specified properties. Users with `admin: true` should get sudo access.

**Solution:**

`vars/users.yml`:
```yaml
---
user_list:
  - name: alice
    groups: developers
    admin: false
  - name: bob
    groups: developers,admins
    admin: true
  - name: charlie
    groups: admins
    admin: true
```

`users-from-vars.yml`:
```yaml
---
- name: Create users from variable file
  hosts: all
  vars_files:
    - vars/users.yml
  tasks:
    - name: Ensure groups exist
      ansible.builtin.group:
        name: "{{ item }}"
        state: present
      loop:
        - developers
        - admins

    - name: Create users
      ansible.builtin.user:
        name: "{{ item.name }}"
        groups: "{{ item.groups }}"
        append: true
        state: present
      loop: "{{ user_list }}"

    - name: Grant sudo to admins
      ansible.builtin.copy:
        content: "{{ item.name }} ALL=(ALL) NOPASSWD: ALL\n"
        dest: "/etc/sudoers.d/{{ item.name }}"
        mode: '0440'
        validate: '/usr/sbin/visudo -cf %s'
      loop: "{{ user_list | selectattr('admin') | list }}"
```

**Verification:**

```bash
ansible-navigator run users-from-vars.yml -m stdout
ansible all -m command -a "id alice"
ansible all -m command -a "id bob"
ansible all -m command -a "sudo -l -U bob"
```

---

### Lab 11: Package Repository Configuration

**Objective:** 2.6 — Manage software repositories

**Task:** Write `configure-repos.yml` that:
1. Configures a custom YUM/DNF repository on all hosts
2. Installs a package from that repo
3. Ensures EPEL is configured on all hosts

**Solution:**

```yaml
---
- name: Configure repositories
  hosts: all
  tasks:
    - name: Configure EPEL repository
      ansible.builtin.dnf:
        name: epel-release
        state: present

    - name: Add custom repository
      ansible.builtin.yum_repository:
        name: custom-repo
        description: Custom Lab Repository
        baseurl: http://control.lab.local/repo
        gpgcheck: false
        enabled: true
        state: present

    - name: Install packages from repos
      ansible.builtin.dnf:
        name:
          - tmux
          - htop
        state: present
```

**Verification:**

```bash
ansible-navigator run configure-repos.yml -m stdout
ansible all -m command -a "dnf repolist"
ansible all -m command -a "rpm -q tmux"
```

---

### Lab 12: Service Management

**Objective:** 2.6 — Manage services

**Task:** Write `service-management.yml` that:
1. Installs `httpd` and `mariadb-server` on appropriate hosts
2. Starts and enables the services
3. Verifies the services are running using `register` and `debug`

**Solution:**

```yaml
---
- name: Manage services on webservers
  hosts: webservers
  tasks:
    - name: Install and start httpd
      ansible.builtin.dnf:
        name: httpd
        state: present

    - name: Enable and start httpd
      ansible.builtin.service:
        name: httpd
        state: started
        enabled: true

    - name: Verify httpd status
      ansible.builtin.command: systemctl is-active httpd
      register: httpd_status
      changed_when: false

    - name: Show httpd status
      ansible.builtin.debug:
        msg: "httpd is {{ httpd_status.stdout }}"

- name: Manage services on dbservers
  hosts: dbservers
  tasks:
    - name: Install mariadb-server
      ansible.builtin.dnf:
        name: mariadb-server
        state: present

    - name: Enable and start mariadb
      ansible.builtin.service:
        name: mariadb
        state: started
        enabled: true
```

**Verification:**

```bash
ansible-navigator run service-management.yml -m stdout
ansible webservers -m command -a "systemctl status httpd"
ansible dbservers -m command -a "systemctl status mariadb"
```

---

### Lab 13: Cron Jobs

**Objective:** 2.6 — Schedule tasks using cron

**Task:** Write `cron-tasks.yml` that:
1. Creates a cron job on all hosts that runs `logger "Ansible managed cron"` every 5 minutes
2. Creates a cron job on webservers that backs up `/var/www/html` daily at 2 AM
3. Creates a cron job for user `devuser1` that runs a cleanup script weekly

**Solution:**

```yaml
---
- name: Manage cron jobs
  hosts: all
  tasks:
    - name: Ansible heartbeat cron
      ansible.builtin.cron:
        name: "Ansible heartbeat"
        minute: "*/5"
        job: 'logger "Ansible managed cron"'
        user: root

- name: Web backup cron
  hosts: webservers
  tasks:
    - name: Daily web backup
      ansible.builtin.cron:
        name: "Daily web backup"
        minute: "0"
        hour: "2"
        job: "tar czf /tmp/web-backup-$(date +\\%F).tar.gz /var/www/html"
        user: root

- name: Devuser cleanup cron
  hosts: all
  tasks:
    - name: Weekly cleanup for devuser1
      ansible.builtin.cron:
        name: "Weekly tmp cleanup"
        special_time: weekly
        job: "find /tmp -user devuser1 -mtime +7 -delete"
        user: devuser1
```

**Verification:**

```bash
ansible-navigator run cron-tasks.yml -m stdout
ansible all -m command -a "crontab -l -u root"
ansible all -m command -a "crontab -l -u devuser1"
```

---

### Lab 14: File Content Management

**Objective:** 2.5, 2.6 — Manage file content

**Task:** Write `file-content.yml` that:
1. Uses `lineinfile` to ensure `SELINUX=enforcing` in `/etc/selinux/config`
2. Uses `blockinfile` to add a custom block to `/etc/hosts`
3. Uses `copy` with `content` to create `/etc/issue` with a login banner
4. Sets correct permissions on all modified files

**Solution:**

```yaml
---
- name: Manage file content
  hosts: all
  tasks:
    - name: Ensure SELinux is enforcing in config
      ansible.builtin.lineinfile:
        path: /etc/selinux/config
        regexp: '^SELINUX='
        line: 'SELINUX=enforcing'

    - name: Add custom hosts block
      ansible.builtin.blockinfile:
        path: /etc/hosts
        block: |
          # Lab custom entries
          192.168.56.100 app.lab.local
          192.168.56.101 db.lab.local
        marker: "# {mark} ANSIBLE MANAGED BLOCK"

    - name: Create login banner
      ansible.builtin.copy:
        content: |
          ==========================================
          WARNING: Authorized access only.
          All activity is monitored and recorded.
          ==========================================
        dest: /etc/issue
        mode: '0644'
```

**Verification:**

```bash
ansible-navigator run file-content.yml -m stdout
ansible all -m command -a "grep SELINUX= /etc/selinux/config"
ansible all -m command -a "cat /etc/hosts"
ansible all -m command -a "cat /etc/issue"
```

---

### Lab 15: Create a Custom Role

**Objective:** 2.7 — Create and work with roles

**Task:** Create a role called `webserver` that:
1. Installs `httpd` and `mod_ssl`
2. Deploys an `index.html` template
3. Starts and enables `httpd`
4. Opens firewall ports 80 and 443
5. Has a handler to restart httpd when config changes
6. Use it in a playbook

**Solution:**

```bash
cd /home/vagrant/ansible
mkdir -p roles
ansible-galaxy init roles/webserver
```

`roles/webserver/tasks/main.yml`:
```yaml
---
- name: Install web packages
  ansible.builtin.dnf:
    name:
      - httpd
      - mod_ssl
    state: present

- name: Deploy index.html from template
  ansible.builtin.template:
    src: index.html.j2
    dest: /var/www/html/index.html
    owner: apache
    group: apache
    mode: '0644'
  notify: Restart httpd

- name: Start and enable httpd
  ansible.builtin.service:
    name: httpd
    state: started
    enabled: true

- name: Open firewall ports
  ansible.posix.firewalld:
    service: "{{ item }}"
    permanent: true
    immediate: true
    state: enabled
  loop:
    - http
    - https
```

`roles/webserver/handlers/main.yml`:
```yaml
---
- name: Restart httpd
  ansible.builtin.service:
    name: httpd
    state: restarted
```

`roles/webserver/templates/index.html.j2`:
```html
<html>
<body>
<h1>Welcome to {{ inventory_hostname }}</h1>
<p>Managed by Ansible</p>
<p>Server IP: {{ ansible_default_ipv4.address }}</p>
<p>OS: {{ ansible_distribution }} {{ ansible_distribution_version }}</p>
</body>
</html>
```

`roles/webserver/defaults/main.yml`:
```yaml
---
http_port: 80
https_port: 443
```

`use-webserver-role.yml`:
```yaml
---
- name: Apply webserver role
  hosts: webservers
  roles:
    - webserver
```

**Verification:**

```bash
ansible-navigator run use-webserver-role.yml -m stdout
ansible webservers -m uri -a "url=http://localhost return_content=yes"
```

---

### Lab 16: Install Roles from Galaxy

**Objective:** 2.7 — Install roles and use them in playbooks

**Task:**
1. Create `requirements.yml` to install `geerlingguy.apache` role
2. Install the role using `ansible-galaxy`
3. Write a playbook that uses the installed role

**Solution:**

`roles/requirements.yml`:
```yaml
---
- name: geerlingguy.apache
  version: "3.2.0"
```

```bash
ansible-galaxy install -r roles/requirements.yml -p roles/
```

`use-galaxy-role.yml`:
```yaml
---
- name: Use Galaxy role
  hosts: webservers
  vars:
    apache_vhosts:
      - servername: "lab.local"
        documentroot: "/var/www/html"
  roles:
    - geerlingguy.apache
```

**Verification:**

```bash
ansible-galaxy list -p roles/
ansible-navigator run use-galaxy-role.yml -m stdout
```

---

### Lab 17: Install and Use Content Collections

**Objective:** 2.7 — Install content collections

**Task:**
1. Create `collections/requirements.yml` for `ansible.posix` and `community.general`
2. Install the collections
3. Write a playbook using modules from both collections

**Solution:**

`collections/requirements.yml`:
```yaml
---
collections:
  - name: ansible.posix
  - name: community.general
```

```bash
ansible-galaxy collection install -r collections/requirements.yml
```

`use-collections.yml`:
```yaml
---
- name: Use modules from collections
  hosts: webservers
  tasks:
    - name: Set SELinux boolean (ansible.posix)
      ansible.posix.seboolean:
        name: httpd_can_network_connect
        state: true
        persistent: true

    - name: Manage firewall (ansible.posix)
      ansible.posix.firewalld:
        service: http
        permanent: true
        immediate: true
        state: enabled

    - name: Set timezone (community.general)
      community.general.timezone:
        name: America/New_York
```

**Verification:**

```bash
ansible-galaxy collection list
ansible-navigator run use-collections.yml -m stdout
ansible webservers -m command -a "getsebool httpd_can_network_connect"
ansible webservers -m command -a "timedatectl"
```

---

### Lab 18: Role with Variables and Dependencies

**Objective:** 2.7 — Advanced role usage

**Task:** Create a role `dbserver` that:
1. Has role dependencies (depends on a `common` role)
2. Uses default variables that can be overridden
3. Installs and configures MariaDB
4. Creates a database using a variable

**Solution:**

Create roles:
```bash
ansible-galaxy init roles/common
ansible-galaxy init roles/dbserver
```

`roles/common/tasks/main.yml`:
```yaml
---
- name: Install common packages
  ansible.builtin.dnf:
    name:
      - vim
      - tree
      - wget
    state: present

- name: Set timezone
  community.general.timezone:
    name: "{{ system_timezone }}"

- name: Ensure chrony is running
  ansible.builtin.service:
    name: chronyd
    state: started
    enabled: true
```

`roles/common/defaults/main.yml`:
```yaml
---
system_timezone: "America/New_York"
```

`roles/dbserver/meta/main.yml`:
```yaml
---
dependencies:
  - role: common
```

`roles/dbserver/tasks/main.yml`:
```yaml
---
- name: Install MariaDB
  ansible.builtin.dnf:
    name:
      - mariadb-server
      - python3-PyMySQL
    state: present

- name: Start and enable MariaDB
  ansible.builtin.service:
    name: mariadb
    state: started
    enabled: true

- name: Open firewall for MariaDB
  ansible.posix.firewalld:
    service: mysql
    permanent: true
    immediate: true
    state: enabled
```

`roles/dbserver/defaults/main.yml`:
```yaml
---
db_name: appdb
db_user: appuser
```

`use-dbserver-role.yml`:
```yaml
---
- name: Apply dbserver role
  hosts: dbservers
  vars:
    db_name: production_db
  roles:
    - dbserver
```

**Verification:**

```bash
ansible-navigator run use-dbserver-role.yml -m stdout
ansible dbservers -m command -a "systemctl is-active mariadb"
ansible dbservers -m command -a "rpm -q mariadb-server"
```

---

### Lab 19: Ansible Vault — Encrypted Files

**Objective:** 2.1, 2.8 — Use Ansible Vault

**Task:**
1. Create a vault-encrypted file `secret.yml` with sensitive variables
2. Write a playbook that uses the encrypted variables
3. Run the playbook with a vault password file

**Solution:**

```bash
# Create vault password file
echo "redhat" > /home/vagrant/ansible/.vault_pass
chmod 600 /home/vagrant/ansible/.vault_pass

# Create encrypted file
ansible-vault create secret.yml --vault-password-file .vault_pass
```

`secret.yml` (encrypted content):
```yaml
---
vault_db_password: "SuperSecret123!"
vault_api_key: "abc-123-def-456"
vault_admin_password: "AdminP@ss2024"
```

`use-vault.yml`:
```yaml
---
- name: Use vault-encrypted variables
  hosts: all
  vars_files:
    - secret.yml
  tasks:
    - name: Create database config file
      ansible.builtin.copy:
        content: |
          DB_HOST=localhost
          DB_NAME=appdb
          DB_PASSWORD={{ vault_db_password }}
          API_KEY={{ vault_api_key }}
        dest: /opt/app.conf
        mode: '0600'
        owner: root
        group: root

    - name: Create admin user with vaulted password
      ansible.builtin.user:
        name: admin
        password: "{{ vault_admin_password | password_hash('sha512') }}"
        state: present
```

Add to `ansible.cfg`:
```ini
vault_password_file = /home/vagrant/ansible/.vault_pass
```

**Verification:**

```bash
ansible-navigator run use-vault.yml -m stdout
ansible-vault view secret.yml --vault-password-file .vault_pass
ansible all -m command -a "cat /opt/app.conf"
ansible all -m command -a "id admin"
```

---

### Lab 20: Ansible Vault — Encrypt String

**Objective:** 2.8 — Inline vault encryption

**Task:**
1. Use `ansible-vault encrypt_string` to encrypt a single variable
2. Embed the encrypted variable directly in a playbook
3. Use multiple vault IDs

**Solution:**

```bash
# Encrypt a string
ansible-vault encrypt_string 'MySecretValue' --name 'my_secret' --vault-password-file .vault_pass
```

`inline-vault.yml`:
```yaml
---
- name: Playbook with inline vault
  hosts: all
  vars:
    my_secret: !vault |
      $ANSIBLE_VAULT;1.1;AES256
      ...encrypted data here...
    plain_var: "This is not secret"
  tasks:
    - name: Use the secret
      ansible.builtin.copy:
        content: "Secret value: {{ my_secret }}\n"
        dest: /tmp/secret-output.txt
        mode: '0600'
```

**Verification:**

```bash
ansible-navigator run inline-vault.yml -m stdout --vault-password-file .vault_pass
ansible all -m command -a "cat /tmp/secret-output.txt"
```

---

### Lab 21: SELinux Management

**Objective:** 2.6, 2.5 — Manage SELinux settings

**Task:** Write `selinux-config.yml` that:
1. Ensures SELinux is in enforcing mode
2. Sets the `httpd_can_network_connect` boolean to on
3. Sets the `httpd_can_network_connect_db` boolean to on
4. Applies file context for a custom web directory
5. Restores SELinux contexts

**Solution:**

```yaml
---
- name: Configure SELinux
  hosts: webservers
  tasks:
    - name: Ensure SELinux is enforcing
      ansible.posix.selinux:
        policy: targeted
        state: enforcing

    - name: Enable httpd_can_network_connect
      ansible.posix.seboolean:
        name: httpd_can_network_connect
        state: true
        persistent: true

    - name: Enable httpd_can_network_connect_db
      ansible.posix.seboolean:
        name: httpd_can_network_connect_db
        state: true
        persistent: true

    - name: Create custom web directory
      ansible.builtin.file:
        path: /custom-web
        state: directory
        mode: '0755'

    - name: Set SELinux file context for custom web dir
      community.general.sefcontext:
        target: '/custom-web(/.*)?'
        setype: httpd_sys_content_t
        state: present

    - name: Restore SELinux contexts
      ansible.builtin.command: restorecon -Rv /custom-web
      changed_when: true
```

**Verification:**

```bash
ansible-navigator run selinux-config.yml -m stdout
ansible webservers -m command -a "getenforce"
ansible webservers -m command -a "getsebool httpd_can_network_connect"
ansible webservers -m command -a "getsebool httpd_can_network_connect_db"
ansible webservers -m command -a "ls -Zd /custom-web"
```

---

### Lab 22: Firewall Management

**Objective:** 2.6 — Manage firewall rules

**Task:** Write `firewall-config.yml` that:
1. Installs `firewalld` on all hosts
2. Starts and enables `firewalld`
3. Opens specific services: `http`, `https`, `mysql` per host group
4. Opens a custom port `8080/tcp` on webservers
5. Configures rich rules for specific source IPs

**Solution:**

```yaml
---
- name: Configure firewall
  hosts: all
  tasks:
    - name: Install firewalld
      ansible.builtin.dnf:
        name: firewalld
        state: present

    - name: Start and enable firewalld
      ansible.builtin.service:
        name: firewalld
        state: started
        enabled: true

- name: Firewall for webservers
  hosts: webservers
  tasks:
    - name: Open web services
      ansible.posix.firewalld:
        service: "{{ item }}"
        permanent: true
        immediate: true
        state: enabled
      loop:
        - http
        - https

    - name: Open custom port 8080
      ansible.posix.firewalld:
        port: 8080/tcp
        permanent: true
        immediate: true
        state: enabled

    - name: Add rich rule for monitoring subnet
      ansible.posix.firewalld:
        rich_rule: 'rule family="ipv4" source address="192.168.56.0/24" port port="9090" protocol="tcp" accept'
        permanent: true
        immediate: true
        state: enabled

- name: Firewall for dbservers
  hosts: dbservers
  tasks:
    - name: Open MySQL service
      ansible.posix.firewalld:
        service: mysql
        permanent: true
        immediate: true
        state: enabled
```

**Verification:**

```bash
ansible-navigator run firewall-config.yml -m stdout
ansible webservers -m command -a "firewall-cmd --list-all"
ansible dbservers -m command -a "firewall-cmd --list-all"
```

---

### Lab 23: RHEL System Role — timesync

**Objective:** 2.8 — Use RHEL system roles

**Task:** Use the `rhel-system-roles.timesync` role to configure NTP on all hosts.

**Solution:**

```bash
# Install the system roles package on control node
sudo dnf install -y rhel-system-roles
```

`timesync-config.yml`:
```yaml
---
- name: Configure NTP with system role
  hosts: all
  vars:
    timesync_ntp_servers:
      - hostname: pool.ntp.org
        iburst: true
      - hostname: time.google.com
        iburst: true
    timesync_ntp_provider: chrony
  roles:
    - rhel-system-roles.timesync
```

**Verification:**

```bash
ansible-navigator run timesync-config.yml -m stdout
ansible all -m command -a "chronyc sources"
ansible all -m command -a "timedatectl"
```

---

### Lab 24: RHEL System Role — selinux

**Objective:** 2.8 — Use RHEL system roles

**Task:** Use the `rhel-system-roles.selinux` role to:
1. Set SELinux to enforcing
2. Enable specific booleans
3. Set file contexts

**Solution:**

```yaml
---
- name: Configure SELinux with system role
  hosts: webservers
  vars:
    selinux_state: enforcing
    selinux_policy: targeted
    selinux_booleans:
      - name: httpd_can_network_connect
        state: true
        persistent: true
      - name: httpd_can_network_connect_db
        state: true
        persistent: true
    selinux_fcontexts:
      - target: '/custom-web(/.*)?'
        setype: httpd_sys_content_t
        state: present
    selinux_restore_dirs:
      - /custom-web
  roles:
    - rhel-system-roles.selinux
```

**Verification:**

```bash
ansible-navigator run selinux-system-role.yml -m stdout
ansible webservers -m command -a "getenforce"
ansible webservers -m command -a "getsebool httpd_can_network_connect"
```

---

### Lab 25: RHEL System Role — network

**Objective:** 2.8 — Use RHEL system roles

**Task:** Use the `rhel-system-roles.network` role to configure a static IP on a secondary interface.

**Solution:**

```yaml
---
- name: Configure network with system role
  hosts: node1.lab.local
  vars:
    network_connections:
      - name: lab-static
        interface_name: eth1
        type: ethernet
        autoconnect: true
        ip:
          address:
            - 10.10.10.1/24
          dhcp4: false
        state: up
  roles:
    - rhel-system-roles.network
```

**Verification:**

```bash
ansible-navigator run network-config.yml -m stdout
ansible node1.lab.local -m command -a "ip addr show"
ansible node1.lab.local -m command -a "nmcli con show"
```

---

### Lab 26: RHEL System Role — storage

**Objective:** 2.8 — Use RHEL system roles for storage

**Task:** Use the `rhel-system-roles.storage` role to create an LVM volume on managed hosts.

**Solution:**

```yaml
---
- name: Configure storage with system role
  hosts: all
  vars:
    storage_pools:
      - name: data_vg
        disks:
          - /dev/loop0
        volumes:
          - name: data_lv
            size: 500m
            fs_type: xfs
            mount_point: /data
            state: present
  roles:
    - rhel-system-roles.storage
```

**Verification:**

```bash
ansible-navigator run storage-config.yml -m stdout
ansible all -m command -a "lvs"
ansible all -m command -a "df -h /data"
ansible all -m command -a "mount | grep data"
```

---

### Lab 27: RHEL System Role — firewall

**Objective:** 2.8 — Use RHEL system roles

**Task:** Use the `rhel-system-roles.firewall` role to configure firewall rules.

**Solution:**

```yaml
---
- name: Configure firewall with system role
  hosts: webservers
  vars:
    firewall:
      - service:
          - http
          - https
        state: enabled
      - port:
          - "8443/tcp"
          - "9090/tcp"
        state: enabled
  roles:
    - rhel-system-roles.firewall
```

**Verification:**

```bash
ansible-navigator run firewall-system-role.yml -m stdout
ansible webservers -m command -a "firewall-cmd --list-all"
```

---

### Lab 28: Jinja2 Templates

**Objective:** 2.8 — Create and use templates

**Task:** Create a Jinja2 template for an Apache virtual host configuration that:
1. Uses variables for server name and document root
2. Uses a `for` loop to generate multiple virtual hosts
3. Uses an `if` conditional for SSL configuration
4. Deploys the template using a playbook

**Solution:**

`templates/vhosts.conf.j2`:
```jinja2
# Managed by Ansible — do not edit manually
{% for vhost in virtual_hosts %}
<VirtualHost *:{{ vhost.port | default(80) }}>
    ServerName {{ vhost.server_name }}
    DocumentRoot {{ vhost.document_root }}

    <Directory {{ vhost.document_root }}>
        AllowOverride All
        Require all granted
    </Directory>

{% if vhost.ssl | default(false) %}
    SSLEngine on
    SSLCertificateFile /etc/pki/tls/certs/{{ vhost.server_name }}.crt
    SSLCertificateKeyFile /etc/pki/tls/private/{{ vhost.server_name }}.key
{% endif %}

    ErrorLog /var/log/httpd/{{ vhost.server_name }}-error.log
    CustomLog /var/log/httpd/{{ vhost.server_name }}-access.log combined
</VirtualHost>

{% endfor %}
```

`templates/hosts.j2`:
```jinja2
# /etc/hosts managed by Ansible
127.0.0.1   localhost localhost.localdomain
::1         localhost localhost.localdomain

{% for host in groups['all'] %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }}  {{ host }} {{ hostvars[host]['ansible_hostname'] }}
{% endfor %}
```

`deploy-templates.yml`:
```yaml
---
- name: Deploy templates
  hosts: webservers
  vars:
    virtual_hosts:
      - server_name: app.lab.local
        document_root: /var/www/app
        port: 80
        ssl: false
      - server_name: secure.lab.local
        document_root: /var/www/secure
        port: 443
        ssl: true
  tasks:
    - name: Create document roots
      ansible.builtin.file:
        path: "{{ item.document_root }}"
        state: directory
        owner: apache
        group: apache
        mode: '0755'
      loop: "{{ virtual_hosts }}"

    - name: Deploy vhosts config
      ansible.builtin.template:
        src: vhosts.conf.j2
        dest: /etc/httpd/conf.d/vhosts.conf
        owner: root
        group: root
        mode: '0644'
      notify: Restart httpd

    - name: Deploy /etc/hosts from template
      ansible.builtin.template:
        src: hosts.j2
        dest: /etc/hosts
        owner: root
        group: root
        mode: '0644'

  handlers:
    - name: Restart httpd
      ansible.builtin.service:
        name: httpd
        state: restarted
```

**Verification:**

```bash
ansible-navigator run deploy-templates.yml -m stdout
ansible webservers -m command -a "cat /etc/httpd/conf.d/vhosts.conf"
ansible webservers -m command -a "cat /etc/hosts"
ansible webservers -m command -a "httpd -t"
```

---

### Lab 29: Error Handling — block/rescue/always

**Objective:** 2.5 — Configure error handling

**Task:** Write `error-handling.yml` that:
1. Uses `block` to attempt installing a package and starting a service
2. Uses `rescue` to handle failure (log the error, install an alternative)
3. Uses `always` to ensure a status report is always generated
4. Uses `ignore_errors` for non-critical tasks

**Solution:**

```yaml
---
- name: Error handling demonstration
  hosts: webservers
  tasks:
    - name: Attempt web server setup
      block:
        - name: Install nginx (may not be available)
          ansible.builtin.dnf:
            name: nginx
            state: present

        - name: Start nginx
          ansible.builtin.service:
            name: nginx
            state: started
            enabled: true

      rescue:
        - name: Log the failure
          ansible.builtin.debug:
            msg: "nginx installation failed, falling back to httpd"

        - name: Install httpd as fallback
          ansible.builtin.dnf:
            name: httpd
            state: present

        - name: Start httpd
          ansible.builtin.service:
            name: httpd
            state: started
            enabled: true

      always:
        - name: Generate status report
          ansible.builtin.copy:
            content: |
              Deployment Report
              Host: {{ inventory_hostname }}
              Date: {{ ansible_date_time.iso8601 }}
              Status: Completed (check which web server is running)
            dest: /tmp/deploy-report.txt
            mode: '0644'

    - name: Non-critical task (may fail)
      ansible.builtin.command: /usr/local/bin/optional-script.sh
      ignore_errors: true
      register: optional_result

    - name: Report optional task status
      ansible.builtin.debug:
        msg: "Optional script {{ 'succeeded' if optional_result.rc == 0 else 'failed (non-critical)' }}"
```

**Verification:**

```bash
ansible-navigator run error-handling.yml -m stdout
ansible webservers -m command -a "cat /tmp/deploy-report.txt"
ansible webservers -m command -a "systemctl is-active httpd"
```

---

## 6. Mock Exam

> **Time Limit: 4 hours**
> Complete all 10 tasks. You may use `ansible-doc` and any docs on the control node.
> Do NOT use the internet.

### Environment

- Control node: `control.lab.local` (192.168.56.10)
- Managed nodes: `node1.lab.local` (192.168.56.20), `node2.lab.local` (192.168.56.21), `node3.lab.local` (192.168.56.22)
- Working directory: `/home/vagrant/ansible`
- All tasks should be performed as the `vagrant` user unless stated otherwise

---

### Task 1: Ansible Configuration (15 min)

Create the file `/home/vagrant/ansible/ansible.cfg` with the following settings:
- Default inventory: `/home/vagrant/ansible/inventory`
- Default remote user: `vagrant`
- Default roles path: `/home/vagrant/ansible/roles`
- Default collections path: `/home/vagrant/ansible/collections`
- Privilege escalation: enabled, method sudo, user root
- Host key checking: disabled
- Vault password file: `/home/vagrant/ansible/.vault_pass`

Create the static inventory `/home/vagrant/ansible/inventory`:
- `node1` in groups `webservers` and `lab`
- `node2` in groups `dbservers` and `lab`
- `node3` in groups `webservers`, `dbservers`, and `lab`

Create the vault password file with the content `exampass`.

Install any required collections (`ansible.posix`, `community.general`).

---

### Task 2: Ad-Hoc Commands (10 min)

Create a script `/home/vagrant/ansible/adhoc.sh` that uses ad-hoc commands to:
1. Create the user `examuser` on all managed nodes
2. Create the directory `/opt/exam` with mode `0755` on all managed nodes
3. Copy the file `/etc/hostname` from the control node to `/tmp/control-name` on all managed nodes

---

### Task 3: Vault-Encrypted Variables (10 min)

Create an Ansible vault-encrypted file `/home/vagrant/ansible/secret.yml` (encrypted with the vault password file) containing:
```yaml
user_password: "Ex@mP@ss123"
db_password: "DbS3cret!"
```

Write a playbook `/home/vagrant/ansible/create-vault-users.yml` that:
- Creates user `vaultuser1` on all hosts with the password from `user_password`
- Creates user `vaultuser2` on `dbservers` with the password from `db_password`

---

### Task 4: Packages and Services Playbook (15 min)

Write `/home/vagrant/ansible/packages.yml` that:
- On `webservers`: installs `httpd` and `mod_ssl`, starts/enables `httpd`
- On `dbservers`: installs `mariadb-server`, starts/enables `mariadb`
- On all hosts: installs `chrony`, starts/enables `chronyd`

---

### Task 5: Jinja2 Template (20 min)

Create a template and playbook:
- Template `/home/vagrant/ansible/templates/server-info.j2` that generates:
  ```
  Hostname: <fqdn>
  IP Address: <default ipv4 address>
  Memory: <total_mb> MB
  OS: <distribution> <version>
  Role: <webserver|dbserver|unknown>
  ```
  The "Role" line should use a Jinja2 conditional based on group membership.

- Playbook `/home/vagrant/ansible/server-info.yml` that deploys this template to `/etc/server-info.txt` on all hosts.

---

### Task 6: Create a Custom Role (20 min)

Create a role `/home/vagrant/ansible/roles/motd` that:
- Deploys a template to `/etc/motd` containing:
  ```
  ================================================
  Welcome to <hostname>
  Managed by Ansible
  Environment: <env_type>   (default: "development")
  ================================================
  ```
- Uses a default variable `env_type` set to `development`

Write `/home/vagrant/ansible/motd.yml` that applies this role to all hosts, overriding `env_type` to `production` for `dbservers`.

---

### Task 7: RHEL System Roles (20 min)

Write `/home/vagrant/ansible/timesync.yml` using the `rhel-system-roles.timesync` role to configure all hosts to use `pool.ntp.org` as NTP server with iburst.

Write `/home/vagrant/ansible/storage.yml` using the `rhel-system-roles.storage` role to create:
- Volume group `exam_vg` on `/dev/loop0`
- Logical volume `exam_lv` of 500 MB with XFS, mounted at `/exam-data`

---

### Task 8: Firewall and SELinux (15 min)

Write `/home/vagrant/ansible/security.yml` that:
- On `webservers`: opens `http` and `https` services in firewall, enables `httpd_can_network_connect` SELinux boolean
- On `dbservers`: opens `mysql` service in firewall
- On all hosts: ensures firewalld is running and enabled

---

### Task 9: Conditional and Loop Playbook (15 min)

Write `/home/vagrant/ansible/conditional-loop.yml` that:
- Defines a list of packages: `httpd`, `mariadb-server`, `php`, `php-mysqlnd`
- Installs ALL packages on hosts that are in BOTH `webservers` AND `dbservers`
- Installs only `httpd` and `php` on hosts in `webservers` only
- Installs only `mariadb-server` on hosts in `dbservers` only
- Creates a report file `/tmp/installed-packages.txt` listing what was installed on each host

---

### Task 10: Error Handling and Handlers (15 min)

Write `/home/vagrant/ansible/robust-deploy.yml` that:
- Uses `block/rescue/always` to deploy a web application:
  - Block: Download a file from `http://control.lab.local/app.tar.gz` to `/opt/app/`, extract it, start httpd
  - Rescue: Create `/opt/app/maintenance.html` with "Site under maintenance", log to `/var/log/deploy-errors.log`
  - Always: Generate `/tmp/deploy-status.txt` with timestamp and result
- Uses a handler to reload httpd when configuration changes

---

### Mock Exam Scoring Guide

| Task | Points | Key Checks |
|---|---|---|
| Task 1 | 30 | ansible.cfg correct, inventory groups correct, vault pass works, collections installed |
| Task 2 | 20 | Script runs successfully, user/dir/file created |
| Task 3 | 30 | Vault file encrypted, users created with correct passwords |
| Task 4 | 30 | Packages installed per group, services running and enabled |
| Task 5 | 30 | Template renders correctly with facts and conditionals |
| Task 6 | 35 | Role structure correct, defaults work, override works |
| Task 7 | 35 | NTP configured, LVM/mount working |
| Task 8 | 30 | Firewall rules applied, SELinux booleans set |
| Task 9 | 30 | Correct packages on correct hosts, report file accurate |
| Task 10 | 30 | Block/rescue/always works, handler triggers |
| **Total** | **300** | **Pass: 210+** |

---

## 7. Exam Tips from Test Takers

> Aggregated from Reddit r/redhat, r/linuxadmin, Red Hat Learning Community, and Medium posts (2024–2026)

### Time Management

- **Read ALL tasks first** before starting. Some tasks build on others.
- **Do the easy tasks first.** Ansible.cfg, inventory, and ad-hoc commands are quick wins — do them in the first 15 minutes.
- **Budget ~12–15 min per task.** With ~17–22 tasks in 4 hours, you can't spend 30 minutes on one.
- **Skip and come back.** If stuck for more than 10 minutes, mark it and move on.
- **Save 15 minutes at the end** to review and run all playbooks one more time.

### Common Pitfalls

1. **YAML indentation errors** — The #1 reason playbooks fail. Use 2-space indentation consistently. Run `--syntax-check` before running.

2. **Forgetting FQCN** — On V9, always use fully qualified collection names. `ansible.builtin.copy` not just `copy`.

3. **Not installing collections** — `firewalld`, `parted`, `sefcontext` are NOT in `ansible-core`. Install `ansible.posix` and `community.general` first.

4. **ansible-navigator mode** — Use `-m stdout` or configure `ansible-navigator.yml` to use stdout mode. The TUI mode wastes time if you're not used to it.

5. **Forgetting `become`** — Most tasks need root. Set it in `ansible.cfg` or per play.

6. **Vault password** — If the task says to use a vault password file, make sure your `ansible.cfg` points to it. Otherwise you'll be prompted every time.

7. **Not testing** — After each task, run the playbook and verify. Don't write 5 playbooks and then test.

8. **System roles variable names** — The variable names for RHEL system roles are specific. Use `ansible-doc` or check `/usr/share/doc/rhel-system-roles/` for examples:
   ```bash
   ls /usr/share/doc/rhel-system-roles/timesync/
   cat /usr/share/doc/rhel-system-roles/timesync/README.md
   ```

9. **SELinux `restorecon`** — After setting file contexts with `sefcontext`, you MUST run `restorecon` for the changes to apply.

10. **Handler ordering** — Handlers run at the end of the play, not immediately after the task. Use `meta: flush_handlers` if you need them to run sooner.

### Important: Partial Credit

The exam is scored on outcomes — **partial credit IS given**. If you cannot complete a complex task fully, complete what you can. A playbook that runs successfully with some tasks correct is better than one that fails entirely. Never leave a task completely blank.

### Strategies That Work

- **Prepare a boilerplate** — Practice writing `ansible.cfg`, inventory, and `ansible-navigator.yml` from memory. This should take <5 minutes on exam day.

- **Use `ansible-doc` heavily** — It's your best friend on the exam. Examples:
  ```bash
  ansible-doc ansible.builtin.user
  ansible-doc ansible.posix.firewalld
  ansible-doc -l | grep keyword
  ```

- **Use `--check` and `--diff`** — Before running for real:
  ```bash
  ansible-navigator run playbook.yml -m stdout --check --diff
  ```

- **Keep your playbooks simple** — Don't over-engineer. If it works and does what the task asks, move on.

- **Know `ansible-galaxy init`** — Memorize the role directory structure. On the exam, you'll need to create roles from scratch.

- **Practice without internet** — The exam has no internet. Practice relying only on `ansible-doc` and local docs.

- **Check `/usr/share/ansible/roles/`** — This is where `rhel-system-roles` are installed. Look at examples there.

- **Copy system role examples** — After installing `rhel-system-roles`, check `/usr/share/doc/rhel-system-roles/<role>/` for example playbooks you can copy and modify. This saves enormous time:
  ```bash
  ls /usr/share/doc/rhel-system-roles/timesync/
  cp /usr/share/doc/rhel-system-roles/storage/example-lvm-playbook.yml .
  ```

- **Convert shell scripts to playbooks** — V9 includes an objective to analyze shell scripts and convert them. Practice reading a `for` loop or `if/then` in bash and writing the equivalent Ansible tasks with `loop` and `when`.

### What People Say is Heavily Tested

Based on community posts from 2024–2026:

1. **ansible.cfg + inventory setup** (almost always the first task)
2. **Ansible Vault** (create, encrypt, use in playbooks)
3. **Jinja2 templates** (with loops and conditionals)
4. **Custom roles** (create from scratch, with handlers and defaults)
5. **RHEL system roles** (especially timesync and storage)
6. **User management** (with passwords, groups, sudo)
7. **Firewall and SELinux** (modules + booleans)
8. **error handling** (block/rescue/always)
9. **Galaxy role installation** (requirements.yml)
10. **Cron jobs** and scheduled tasks

---

## 8. Essential Commands Quick Reference

### Ansible Core Commands

```bash
# Check connectivity
ansible all -m ping

# Run ad-hoc command
ansible <group> -m <module> -a "<args>"
ansible all -m command -a "uptime"
ansible webservers -m dnf -a "name=httpd state=present"
ansible all -m copy -a "src=/tmp/file dest=/tmp/file"

# Run playbook (V9 style)
ansible-navigator run playbook.yml -m stdout
ansible-navigator run playbook.yml -m stdout --check --diff
ansible-navigator run playbook.yml -m stdout -e "var=value"

# Run playbook (also works on V9)
ansible-playbook playbook.yml
ansible-playbook playbook.yml --syntax-check
ansible-playbook playbook.yml --check --diff
ansible-playbook playbook.yml --limit webservers
ansible-playbook playbook.yml --tags "install,configure"

# Show inventory
ansible-navigator inventory -m stdout --list
ansible-navigator inventory -m stdout --graph

# Module documentation
ansible-doc ansible.builtin.copy
ansible-doc ansible.posix.firewalld
ansible-doc -l                          # List all modules
ansible-doc -l | grep firewall          # Search modules
ansible-doc -l -t role                  # List roles
```

### Ansible Vault

```bash
# Create encrypted file
ansible-vault create secret.yml
ansible-vault create secret.yml --vault-password-file .vault_pass

# Edit encrypted file
ansible-vault edit secret.yml

# View encrypted file
ansible-vault view secret.yml

# Encrypt existing file
ansible-vault encrypt plain.yml

# Decrypt file
ansible-vault decrypt secret.yml

# Encrypt a string (inline vault)
ansible-vault encrypt_string 'secret_value' --name 'var_name'

# Rekey (change password)
ansible-vault rekey secret.yml
```

### Ansible Galaxy

```bash
# Initialize a new role
ansible-galaxy init roles/myrole

# Install role from Galaxy
ansible-galaxy install geerlingguy.apache

# Install roles from requirements file
ansible-galaxy install -r roles/requirements.yml -p roles/

# Install collections
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.general
ansible-galaxy collection install -r collections/requirements.yml

# List installed roles/collections
ansible-galaxy list
ansible-galaxy collection list
```

### RHEL System Roles

```bash
# Install
sudo dnf install -y rhel-system-roles

# List available roles
ls /usr/share/ansible/roles/

# View documentation
ls /usr/share/doc/rhel-system-roles/
cat /usr/share/doc/rhel-system-roles/timesync/README.md

# Available roles:
#   rhel-system-roles.timesync
#   rhel-system-roles.selinux
#   rhel-system-roles.network
#   rhel-system-roles.firewall
#   rhel-system-roles.storage
#   rhel-system-roles.kdump
#   rhel-system-roles.logging
#   rhel-system-roles.metrics
#   rhel-system-roles.tlog
#   rhel-system-roles.certificate
```

### Troubleshooting

```bash
# Verbose output
ansible-navigator run playbook.yml -m stdout -v    # minimal
ansible-navigator run playbook.yml -m stdout -vvv  # detailed
ansible-navigator run playbook.yml -m stdout -vvvv # connection debug

# Syntax check
ansible-navigator run playbook.yml -m stdout --syntax-check

# Dry run
ansible-navigator run playbook.yml -m stdout --check

# Step through tasks
ansible-playbook playbook.yml --step

# Start at specific task
ansible-playbook playbook.yml --start-at-task "Task Name"

# List tasks in playbook
ansible-playbook playbook.yml --list-tasks

# List hosts targeted by playbook
ansible-playbook playbook.yml --list-hosts

# Check ansible configuration
ansible --version
ansible-config dump --only-changed

# Test module availability
ansible-doc -l | grep modulename
```

### Common Module Quick Reference

| Module (FQCN) | Purpose | Key Parameters |
|---|---|---|
| `ansible.builtin.copy` | Copy files to remote | `src`, `dest`, `content`, `mode`, `owner` |
| `ansible.builtin.template` | Deploy Jinja2 templates | `src`, `dest`, `mode`, `owner` |
| `ansible.builtin.file` | Manage files/dirs | `path`, `state`, `mode`, `owner`, `group` |
| `ansible.builtin.lineinfile` | Manage lines in files | `path`, `regexp`, `line`, `state` |
| `ansible.builtin.blockinfile` | Manage blocks in files | `path`, `block`, `marker` |
| `ansible.builtin.dnf` | Package management | `name`, `state` (present/absent/latest) |
| `ansible.builtin.service` | Service management | `name`, `state`, `enabled` |
| `ansible.builtin.user` | User management | `name`, `uid`, `group`, `groups`, `password`, `state` |
| `ansible.builtin.group` | Group management | `name`, `gid`, `state` |
| `ansible.builtin.cron` | Cron jobs | `name`, `minute`, `hour`, `job`, `user`, `special_time` |
| `ansible.builtin.command` | Run commands | `cmd` (no shell features) |
| `ansible.builtin.shell` | Run shell commands | `cmd` (supports pipes, redirects) |
| `ansible.builtin.get_url` | Download files | `url`, `dest`, `mode` |
| `ansible.builtin.uri` | HTTP requests | `url`, `method`, `body`, `return_content` |
| `ansible.builtin.debug` | Print messages | `msg`, `var` |
| `ansible.builtin.yum_repository` | Manage repos | `name`, `description`, `baseurl`, `gpgcheck` |
| `ansible.builtin.mount` | Manage mounts | `path`, `src`, `fstype`, `state` |
| `ansible.posix.firewalld` | Firewall rules | `service`, `port`, `permanent`, `immediate`, `state` |
| `ansible.posix.seboolean` | SELinux booleans | `name`, `state`, `persistent` |
| `ansible.posix.selinux` | SELinux mode | `state`, `policy` |
| `community.general.sefcontext` | SELinux file contexts | `target`, `setype`, `state` |
| `community.general.parted` | Disk partitions | `device`, `number`, `state`, `part_type` |
| `community.general.lvg` | LVM volume groups | `vg`, `pvs`, `state` |
| `community.general.lvol` | LVM logical volumes | `vg`, `lv`, `size`, `state` |
| `community.general.timezone` | Set timezone | `name` |

---

## 9. Recommended Resources

### Official Red Hat

- [EX294 Exam Page & Objectives](https://www.redhat.com/en/services/training/ex294-red-hat-certified-engineer-rhce-exam-red-hat-enterprise-linux)
- [Red Hat Enterprise Linux Automation with Ansible (AU294) Course](https://www.redhat.com/en/services/training/rh294-red-hat-linux-automation-with-ansible)
- [Red Hat Learning Community — EX294 Discussions](https://learn.redhat.com/t5/Automation-Management-Ansible/ct-p/automation-management)
- [Ansible Documentation](https://docs.ansible.com/ansible/latest/)

### Books

- **Sander van Vugt** — *Red Hat RHCE 8 (EX294) Cert Guide* (Pearson) — The gold standard RHCE prep book. V8 content but most concepts apply to V9.
- **Waleed Hassan** — *Red Hat RHCE 9 (EX294) Capsules: Certification Guide* — Updated for RHEL 9.
- **Ghada Atef** — *Mastering the RHCE EX294 Exam 2025* — Recent publication covering both RHEL 8 and 9.

### Video Courses

- **Sander van Vugt** — [RHCE EX294 Complete Video Course](https://www.sandervanvugt.com/) — 9-hour comprehensive course with live demos
- **Pluralsight** — [RHCE: Red Hat Certified Engineer (EX294) Path](https://www.pluralsight.com/paths/rhce-red-hat-certified-engineer-ex294)
- **Pluralsight** — [What's New in RHEL 9 for RHCE EX294](https://www.pluralsight.com/courses/whats-new-rhel9-rhce-ex294) — Specifically covers V8→V9 changes

### GitHub Repos (Practice Labs)

- [RedHatRanger/RHCE9Vagrant](https://github.com/RedHatRanger/RHCE9Vagrant) — Vagrant-based RHCE 9 lab environment with practice tasks
- [Abdulhamid97Mousa/RHCE-EX294](https://github.com/Abdulhamid97Mousa/RHCE-EX294) — Study guide and exam questions
- [mateuszstompor/rhce-ex294-exam](https://github.com/mateuszstompor/rhce-ex294-exam) — Practice exercises for EX294
- [eu-devops/rhce-ex294-v9](https://github.com/eu-devops/rhce-ex294-v9) — Lab environment and recap for V9
- [Hexadecimalz/RHCE-Study](https://github.com/Hexadecimalz/RHCE-Study) — RHCE Study Group notes
- [waseem-h RHCE Practice Exam Gist](https://gist.github.com/waseem-h/6793ba3328f27df1a815402710acb3ff) — Practice exam in a single markdown file

### Practice Exams

- [Lisenet — Ansible Sample Exam for EX294](https://www.lisenet.com/2019/ansible-sample-exam-for-ex294/) — Widely regarded as the best free practice exam (18 tasks, no answers provided — forces you to problem-solve)
- [Geuni's Practice Exam for RHCE 9](https://www.geuni.tech/en/linux/rhce_practice) — 17 tasks specifically updated for V9, covers `redhat.rhel_system_roles` collection format
- [SeiMaxim — Ansible Sample Exam Questions and Answers](https://www.seimaxim.com/kb/ansible-sample-exam-questions-and-answers-for-rhce-ex294)
- [rhce-practice-exam.org](https://rhce-practice-exam.org/study-resources.html) — Study resources and practice scenarios
- [Tekneed — RHCE/EX294 V9 Practice Questions](https://tekneed.com/rhce-ex294-v9-exam-practice-questions-ansible/) — Free introductory set with premium options

### Free Hands-On Labs

- [Red Hat Ansible Workshop](https://labs.demoredhat.com/exercises/ansible_rhel/) — Official Red Hat free hands-on exercises

### Community

- [Reddit r/redhat](https://www.reddit.com/r/redhat/) — Active exam discussion and tips
- [Reddit r/linuxadmin](https://www.reddit.com/r/linuxadmin/) — Sysadmin community with RHCE threads
- [Red Hat Learning Community](https://learn.redhat.com/) — Official forums with verified answers
  - [EX294V9 — ansible-navigator discussion](https://learn.redhat.com/t5/General/EX294V9-ansible-navigator/td-p/41166)
  - [EX294V9K Objectives — Ansible Navigator and Inventories](https://learn.redhat.com/t5/Automation-Management-Ansible/RHCE-EX294V9K-Objectives-Ansible-Navigator-and-Inventories/td-p/42513)
  - [About rhel_system_roles on the EX294 v9 exam](https://learn.redhat.com/t5/General/About-rhel-system-roles-on-the-EX294-v9-exam/td-p/39155)
- [Medium — "How I Passed RHCE EX294"](https://medium.com/@daryl-goh/how-i-passed-the-red-hat-certified-engineer-rhce-ex294-exam-78a8ef3b0a4b) — Detailed pass story

---

> **Good luck on the exam!** The key is hands-on practice. If you can complete all 29 labs and the mock exam in this guide without looking at the solutions, you are well-prepared.
