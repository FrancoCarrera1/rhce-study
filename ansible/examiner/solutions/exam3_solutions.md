# Practice Exam 3 - Reference Solutions

**Working directory:** `/home/vagrant/exam`
**Vault password:** `practice99`
**Vault password file:** `/home/vagrant/exam/.vault_key`

All playbooks use FQCNs. Run from `/home/vagrant/exam` with the `ansible.cfg` in place.

---

## Task 1: Configure Ansible

**Points: 30**

### Step 1 — Create directory structure

```bash
mkdir -p /home/vagrant/exam/{roles,collections,templates,group_vars}
```

### Step 2 — Create `ansible.cfg`

File: `/home/vagrant/exam/ansible.cfg`

```ini
[defaults]
inventory            = /home/vagrant/exam/inventory
remote_user          = vagrant
roles_path           = /home/vagrant/exam/roles
collections_path     = /home/vagrant/exam/collections
host_key_checking    = False
vault_password_file  = /home/vagrant/exam/.vault_key

[privilege_escalation]
become      = True
become_method = sudo
become_user = root
```

### Step 3 — Create static inventory

File: `/home/vagrant/exam/inventory`

```ini
[webservers]
node1.lab.local
node3.lab.local

[dbservers]
node2.lab.local
node3.lab.local

[lab]
node1.lab.local
node2.lab.local
node3.lab.local
node4.lab.local
node5.lab.local

[workers:children]
lab
```

> **Note:** The exam checks for `[webservers]`, `[dbservers]`, and the nodes node1-node5. node4 and node5 are in `lab` but not in webservers or dbservers — this matches the conditional logic required in Task 9.

### Step 4 — Create vault password file

```bash
echo 'practice99' > /home/vagrant/exam/.vault_key
chmod 600 /home/vagrant/exam/.vault_key
```

### Step 5 — Install collections

```bash
ansible-galaxy collection install ansible.posix \
  -p /home/vagrant/exam/collections

ansible-galaxy collection install community.general \
  -p /home/vagrant/exam/collections
```

**Verify:**

```bash
ansible --version
ansible-inventory --list
ansible-galaxy collection list --collections-path /home/vagrant/exam/collections
```

---

## Task 2: Ad-Hoc Commands Script

**Points: 20**

File: `/home/vagrant/exam/adhoc.sh`

```bash
#!/bin/bash
# Ad-hoc commands targeting all managed nodes.
# Run from /home/vagrant/exam where ansible.cfg resides.

INVENTORY=/home/vagrant/exam/inventory

# 1. Create user 'labuser' on all managed nodes
ansible all -i "${INVENTORY}" \
  -m ansible.builtin.user \
  -a "name=labuser state=present"

# 2. Create directory /opt/lab with mode 0755
ansible all -i "${INVENTORY}" \
  -m ansible.builtin.file \
  -a "path=/opt/lab state=directory mode=0755 owner=root group=root"

# 3. Copy the remote /etc/hostname to /tmp/control-name (remote_src copies on the target)
ansible all -i "${INVENTORY}" \
  -m ansible.builtin.copy \
  -a "src=/etc/hostname dest=/tmp/control-name remote_src=yes"
```

```bash
chmod +x /home/vagrant/exam/adhoc.sh
```

**Run:**

```bash
cd /home/vagrant/exam && bash adhoc.sh
```

> **Key point:** `remote_src=yes` tells the copy module to read the source file from the *remote* node (not the control node), so each node copies its own `/etc/hostname` to `/tmp/control-name`.

---

## Task 3: Vault-Encrypted Variables and User Creation

**Points: 30**

### Step 1 — Create the encrypted vault file

```bash
cd /home/vagrant/exam

ansible-vault create secret.yml
```

When the editor opens, enter:

```yaml
app_password: "Appl!c@t10n"
db_secret: "Dat@b@se99"
```

Save and quit. Because `vault_password_file` is set in `ansible.cfg`, the vault password (`practice99`) is read automatically.

Alternatively, create it non-interactively:

```bash
cat > /tmp/vault_content.yml << 'EOF'
app_password: "Appl!c@t10n"
db_secret: "Dat@b@se99"
EOF

ansible-vault encrypt /tmp/vault_content.yml \
  --vault-password-file /home/vagrant/exam/.vault_key \
  --output /home/vagrant/exam/secret.yml

rm /tmp/vault_content.yml
```

**Verify:**

```bash
ansible-vault view /home/vagrant/exam/secret.yml
```

### Step 2 — Create the playbook

File: `/home/vagrant/exam/create-vault-users.yml`

```yaml
---
- name: Create vault-protected users on all managed hosts
  hosts: all
  vars_files:
    - secret.yml

  tasks:
    - name: Create svcuser1 on all managed hosts
      ansible.builtin.user:
        name: svcuser1
        password: "{{ app_password | password_hash('sha512') }}"
        shell: /bin/bash
        state: present

- name: Create vault-protected users on dbservers only
  hosts: dbservers
  vars_files:
    - secret.yml

  tasks:
    - name: Create svcuser2 on dbservers
      ansible.builtin.user:
        name: svcuser2
        password: "{{ db_secret | password_hash('sha512') }}"
        shell: /bin/bash
        state: present
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook create-vault-users.yml
```

> **Note:** The vault password file is configured in `ansible.cfg`, so `--vault-password-file` is not needed on the command line. svcuser2 must NOT exist on node1 (webservers only), which is ensured by scoping the second play to `hosts: dbservers`.

---

## Task 4: Install Packages and Manage Services

**Points: 30**

File: `/home/vagrant/exam/packages.yml`

```yaml
---
- name: Install and configure web server packages
  hosts: webservers
  tasks:
    - name: Install httpd and mod_ssl
      ansible.builtin.dnf:
        name:
          - httpd
          - mod_ssl
        state: present

    - name: Start and enable httpd service
      ansible.builtin.service:
        name: httpd
        state: started
        enabled: true

- name: Install and configure database server packages
  hosts: dbservers
  tasks:
    - name: Install mariadb-server
      ansible.builtin.dnf:
        name: mariadb-server
        state: present

    - name: Start and enable mariadb service
      ansible.builtin.service:
        name: mariadb
        state: started
        enabled: true

- name: Install time synchronization on all lab hosts
  hosts: lab
  tasks:
    - name: Install chrony
      ansible.builtin.dnf:
        name: chrony
        state: present

    - name: Start and enable chronyd service
      ansible.builtin.service:
        name: chronyd
        state: started
        enabled: true
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook packages.yml
```

---

## Task 5: Deploy Server Info with a Jinja2 Template

**Points: 30**

### Step 1 — Create the Jinja2 template

File: `/home/vagrant/exam/templates/server-info.j2`

```jinja2
Hostname: {{ ansible_fqdn }}
IP Address: {{ ansible_default_ipv4.address }}
Memory: {{ ansible_memtotal_mb }} MB
OS: {{ ansible_distribution }} {{ ansible_distribution_version }}
Role: {% if 'webservers' in group_names %}webserver{% elif 'dbservers' in group_names %}dbserver{% else %}unknown{% endif %}
```

### Step 2 — Create the playbook

File: `/home/vagrant/exam/server-info.yml`

```yaml
---
- name: Deploy server information file using Jinja2 template
  hosts: lab
  tasks:
    - name: Deploy server-info.txt from template
      ansible.builtin.template:
        src: templates/server-info.j2
        dest: /etc/server-info.txt
        owner: root
        group: root
        mode: '0644'
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook server-info.yml
```

**Verify on node1 (webservers):**

```bash
ansible node1.lab.local -m ansible.builtin.command -a "cat /etc/server-info.txt"
# Role: webserver

ansible node2.lab.local -m ansible.builtin.command -a "cat /etc/server-info.txt"
# Role: dbserver

ansible node4.lab.local -m ansible.builtin.command -a "cat /etc/server-info.txt"
# Role: unknown
```

---

## Task 6: Create and Apply a Custom Role

**Points: 35**

### Step 1 — Create role directory structure

```bash
mkdir -p /home/vagrant/exam/roles/motd/{tasks,defaults,templates}
```

### Step 2 — Role defaults

File: `/home/vagrant/exam/roles/motd/defaults/main.yml`

```yaml
---
env_type: "development"
```

### Step 3 — Role template

File: `/home/vagrant/exam/roles/motd/templates/motd.j2`

```jinja2
================================================
Welcome to {{ ansible_hostname }}
Managed by Ansible
Environment: {{ env_type }}
================================================
```

### Step 4 — Role tasks

File: `/home/vagrant/exam/roles/motd/tasks/main.yml`

```yaml
---
- name: Deploy MOTD from template
  ansible.builtin.template:
    src: motd.j2
    dest: /etc/motd
    owner: root
    group: root
    mode: '0644'
```

### Step 5 — Group variables for dbservers

File: `/home/vagrant/exam/group_vars/dbservers.yml`

```yaml
---
env_type: "production"
```

### Step 6 — Create the playbook

File: `/home/vagrant/exam/motd.yml`

```yaml
---
- name: Apply motd role to all lab hosts
  hosts: lab
  roles:
    - motd
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook motd.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command -a "cat /etc/motd"
# Contains: Welcome to node1, Environment: development

ansible node2.lab.local -m ansible.builtin.command -a "cat /etc/motd"
# Contains: Welcome to node2, Environment: production
```

> **Key point:** `group_vars/dbservers.yml` overrides the role default `env_type` to `"production"` for node2 and node3 (both in dbservers). The `group_vars/` directory sits alongside `ansible.cfg` in `/home/vagrant/exam/`.

---

## Task 7: Use RHEL System Roles

**Points: 35**

### Part A — Time Synchronization

First, install the system roles collection if not already present:

```bash
ansible-galaxy collection install fedora.linux_system_roles \
  -p /home/vagrant/exam/collections
```

File: `/home/vagrant/exam/timesync.yml`

```yaml
---
- name: Configure time synchronization using system role
  hosts: lab
  vars:
    timesync_ntp_servers:
      - hostname: pool.ntp.org
        iburst: yes
  roles:
    - fedora.linux_system_roles.timesync
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook timesync.yml
```

### Part B — Storage with community.general

File: `/home/vagrant/exam/storage.yml`

```yaml
---
- name: Configure LVM storage on lab hosts
  hosts: lab

  tasks:
    - name: Create volume group exam_vg on /dev/loop0
      community.general.lvg:
        vg: exam_vg
        pvs: /dev/loop0
        state: present
      ignore_errors: yes

    - name: Create logical volume exam_lv (500m) in exam_vg
      community.general.lvol:
        vg: exam_vg
        lv: exam_lv
        size: 500m
        state: present
      ignore_errors: yes

    - name: Create XFS filesystem on exam_lv
      ansible.builtin.filesystem:
        fstype: xfs
        dev: /dev/exam_vg/exam_lv
      ignore_errors: yes

    - name: Create /exam-data mount point
      ansible.builtin.file:
        path: /exam-data
        state: directory
        mode: '0755'

    - name: Mount /dev/exam_vg/exam_lv at /exam-data
      ansible.posix.mount:
        path: /exam-data
        src: /dev/exam_vg/exam_lv
        fstype: xfs
        state: mounted
      ignore_errors: yes
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook storage.yml
```

> **Note:** `ignore_errors: yes` is required per the task description because loop devices may not be available in all lab environments. The `ansible.posix.mount` module handles the `/etc/fstab` entry automatically when `state: mounted` is used.

---

## Task 8: Configure Firewall and SELinux

**Points: 30**

File: `/home/vagrant/exam/security.yml`

```yaml
---
- name: Ensure firewalld is installed and running on all lab hosts
  hosts: lab
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

- name: Configure firewall and SELinux for web servers
  hosts: webservers
  tasks:
    - name: Open http service in firewall (permanent)
      ansible.posix.firewalld:
        service: http
        permanent: true
        state: enabled
        immediate: true

    - name: Open https service in firewall (permanent)
      ansible.posix.firewalld:
        service: https
        permanent: true
        state: enabled
        immediate: true

    - name: Enable httpd_can_network_connect SELinux boolean (persistent)
      ansible.posix.seboolean:
        name: httpd_can_network_connect
        state: true
        persistent: true

- name: Configure firewall for database servers
  hosts: dbservers
  tasks:
    - name: Open mysql service in firewall (permanent)
      ansible.posix.firewalld:
        service: mysql
        permanent: true
        state: enabled
        immediate: true
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook security.yml
```

> **Note:** The `immediate: true` parameter applies the rule to the running firewall without requiring a reload. Without it, only the permanent configuration changes and the check `firewall-cmd --list-services` (which reads the running config) would fail.

---

## Task 9: Conditionals and Loops

**Points: 30**

File: `/home/vagrant/exam/conditional-loop.yml`

```yaml
---
- name: Install packages based on group membership using conditionals and loops
  hosts: lab

  vars:
    web_db_packages:
      - httpd
      - mariadb-server
      - php
      - php-mysqlnd

    web_only_packages:
      - httpd
      - php

    db_only_packages:
      - mariadb-server

  tasks:
    - name: Install packages for hosts in BOTH webservers AND dbservers
      ansible.builtin.dnf:
        name: "{{ item }}"
        state: present
      loop: "{{ web_db_packages }}"
      when:
        - "'webservers' in group_names"
        - "'dbservers' in group_names"

    - name: Install packages for webservers-ONLY hosts (not dbservers)
      ansible.builtin.dnf:
        name: "{{ item }}"
        state: present
      loop: "{{ web_only_packages }}"
      when:
        - "'webservers' in group_names"
        - "'dbservers' not in group_names"

    - name: Install packages for dbservers-ONLY hosts (not webservers)
      ansible.builtin.dnf:
        name: "{{ item }}"
        state: present
      loop: "{{ db_only_packages }}"
      when:
        - "'dbservers' in group_names"
        - "'webservers' not in group_names"

    - name: Build installed packages list for web+db hosts
      ansible.builtin.copy:
        content: "{{ web_db_packages | join('\n') }}\n"
        dest: /tmp/installed-packages.txt
        mode: '0644'
      when:
        - "'webservers' in group_names"
        - "'dbservers' in group_names"

    - name: Build installed packages list for webservers-only hosts
      ansible.builtin.copy:
        content: "{{ web_only_packages | join('\n') }}\n"
        dest: /tmp/installed-packages.txt
        mode: '0644'
      when:
        - "'webservers' in group_names"
        - "'dbservers' not in group_names"

    - name: Build installed packages list for dbservers-only hosts
      ansible.builtin.copy:
        content: "{{ db_only_packages | join('\n') }}\n"
        dest: /tmp/installed-packages.txt
        mode: '0644'
      when:
        - "'dbservers' in group_names"
        - "'webservers' not in group_names"

    - name: Create empty installed-packages.txt for other lab hosts
      ansible.builtin.copy:
        content: "No extra packages installed\n"
        dest: /tmp/installed-packages.txt
        mode: '0644'
      when:
        - "'webservers' not in group_names"
        - "'dbservers' not in group_names"
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook conditional-loop.yml
```

**Expected results:**
- node1 (webservers only): installs `httpd`, `php`
- node2 (dbservers only): installs `mariadb-server`
- node3 (webservers + dbservers): installs `httpd`, `mariadb-server`, `php`, `php-mysqlnd`
- node4, node5 (lab only): no extra packages

---

## Task 10: Error Handling with Block/Rescue/Always

**Points: 30**

File: `/home/vagrant/exam/robust-deploy.yml`

```yaml
---
- name: Robust deployment with block/rescue/always error handling
  hosts: webservers

  handlers:
    - name: reload httpd
      ansible.builtin.service:
        name: httpd
        state: reloaded

  tasks:
    - name: Application deployment with error handling
      block:
        - name: Create /opt/app directory
          ansible.builtin.file:
            path: /opt/app
            state: directory
            mode: '0755'
            owner: root
            group: root
          notify: reload httpd

        - name: Download app.tar.gz (expected to fail — demo rescue)
          ansible.builtin.get_url:
            url: http://control.lab.local/app.tar.gz
            dest: /opt/app/app.tar.gz
            timeout: 10

      rescue:
        - name: Create maintenance page (rescue block)
          ansible.builtin.copy:
            content: "Site under maintenance\n"
            dest: /opt/app/maintenance.html
            owner: root
            group: root
            mode: '0644'

        - name: Log error with timestamp to deploy-errors.log
          ansible.builtin.lineinfile:
            path: /var/log/deploy-errors.log
            line: "[{{ ansible_date_time.iso8601 }}] Deployment failed on {{ ansible_hostname }} — download of app.tar.gz failed"
            create: yes
            mode: '0644'

      always:
        - name: Write deploy status file (always runs)
          ansible.builtin.copy:
            content: |
              Deployment process completed on {{ ansible_hostname }}
              Date: {{ ansible_date_time.date }}
              Time: {{ ansible_date_time.time }}
              Status: See /var/log/deploy-errors.log for any errors.
            dest: /tmp/deploy-status.txt
            mode: '0644'
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook robust-deploy.yml
```

**Expected behavior:**
1. `/opt/app` directory is created successfully
2. The `get_url` task fails (no file at that URL) — this triggers the `rescue` block
3. `rescue` creates `/opt/app/maintenance.html` and logs to `/var/log/deploy-errors.log`
4. `always` writes `/tmp/deploy-status.txt` regardless of success/failure
5. The `reload httpd` handler fires because the directory task (which succeeded in the block) notified it

> **Key points:**
> - Handlers defined at the play level are available throughout the play including in `block`/`rescue`/`always` sections.
> - The handler notification from the successful `file` task in `block` is still queued even after `rescue` runs; handlers fire at the end of the play.
> - `ansible.builtin.lineinfile` with `create: yes` will create the log file if it does not exist.
> - `ansible_date_time` is populated automatically by the gather_facts step (enabled by default).
