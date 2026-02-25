# Bonus Exam — Topic Review - Reference Solutions

**Working directory:** `/home/vagrant/exam`
**Vault password:** `ansible123`
**Vault password file:** `/home/vagrant/exam/vault_key`

**Inventory groups:**
- `webservers`: node1, node2
- `dbservers`: node3, node4
- `balancers`: node5
- `lab`: node1–node5 (all managed nodes)

All playbooks use FQCNs. Run from `/home/vagrant/exam` with the `ansible.cfg` in place.

---

## Task 1: Install and Configure Ansible

**Points: 20**

### Step 1 — Create directory structure

```bash
mkdir -p /home/vagrant/exam/{roles,collections,templates,group_vars}
```

### Step 2 — Create `ansible.cfg`

File: `/home/vagrant/exam/ansible.cfg`

```ini
[defaults]
inventory         = /home/vagrant/exam/inventory
remote_user       = vagrant
roles_path        = /home/vagrant/exam/roles
host_key_checking = False

[privilege_escalation]
become        = True
become_method = sudo
become_user   = root
```

### Step 3 — Create the inventory

File: `/home/vagrant/exam/inventory`

```ini
[webservers]
node1.lab.local
node2.lab.local

[dbservers]
node3.lab.local
node4.lab.local

[balancers]
node5.lab.local

[lab:children]
webservers
dbservers
balancers

[control]
control.lab.local
```

**Verify:**

```bash
ansible --version
ansible-inventory --list
ansible lab -m ansible.builtin.ping
```

---

## Task 2: Configure Yum Repositories

**Points: 15**

File: `/home/vagrant/exam/yum_repo.yml`

```yaml
---
- name: Configure AlmaLinux 9 yum repositories on all lab group nodes
  hosts: lab

  tasks:
    - name: Configure BaseOS repository
      ansible.builtin.yum_repository:
        name: BaseOS
        description: "AlmaLinux 9 BaseOS"
        baseurl: "https://repo.almalinux.org/almalinux/9/BaseOS/aarch64/os/"
        gpgcheck: true
        gpgkey: "https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-9"
        enabled: true
        state: present

    - name: Configure AppStream repository
      ansible.builtin.yum_repository:
        name: AppStream
        description: "AlmaLinux 9 AppStream"
        baseurl: "https://repo.almalinux.org/almalinux/9/AppStream/aarch64/os/"
        gpgcheck: true
        gpgkey: "https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-9"
        enabled: true
        state: present
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook yum_repo.yml
```

> **Note:** `ansible.builtin.yum_repository` creates `.repo` files under `/etc/yum.repos.d/`. The check in the exam looks for either `BaseOS.repo` or `yum repolist | grep baseos`, both of which are satisfied by this approach.

---

## Task 3: Install Packages

**Points: 15**

File: `/home/vagrant/exam/packages.yml`

```yaml
---
- name: Install httpd and mod_ssl on webservers group
  hosts: webservers
  tasks:
    - name: Install web server packages
      ansible.builtin.dnf:
        name:
          - httpd
          - mod_ssl
        state: present

- name: Install mariadb-server on dbservers group
  hosts: dbservers
  tasks:
    - name: Install database server package
      ansible.builtin.dnf:
        name: mariadb-server
        state: present

- name: Install Development Tools package group on node5
  hosts: node5.lab.local
  tasks:
    - name: Install Development Tools package group
      ansible.builtin.dnf:
        name: "@Development Tools"
        state: present
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook packages.yml
```

> **Note:** Package groups are referenced with the `@` prefix in `ansible.builtin.dnf`. The `@Development Tools` syntax is equivalent to `yum groupinstall "Development Tools"`.

---

## Task 4: Use the timesync RHEL System Role

**Points: 20**

First, install the collection if not already present:

```bash
ansible-galaxy collection install fedora.linux_system_roles \
  -p /home/vagrant/exam/collections
```

File: `/home/vagrant/exam/timesync.yml`

```yaml
---
- name: Configure NTP time synchronization on all managed nodes
  hosts: lab
  vars:
    timesync_ntp_provider: chrony
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

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command -a "systemctl is-active chronyd"
ansible node1.lab.local -m ansible.builtin.command -a "grep pool.ntp.org /etc/chrony.conf"
```

> **Note:** The `timesync_ntp_provider: chrony` variable instructs the role to configure chrony as the NTP backend. The role installs chrony if not already present, configures `/etc/chrony.conf`, and ensures the service is started and enabled.

---

## Task 5: Use Ansible Vault

**Points: 15**

### Step 1 — Create the vault password file

```bash
echo 'ansible123' > /home/vagrant/exam/vault_key
chmod 600 /home/vagrant/exam/vault_key
```

### Step 2 — Create the encrypted vault file

```bash
cat > /tmp/secret_content.yml << 'EOF'
dev_pw: devAccess7
prod_pw: prodAccess7
EOF

ansible-vault encrypt /tmp/secret_content.yml \
  --vault-password-file /home/vagrant/exam/vault_key \
  --output /home/vagrant/exam/secret.yml

rm /tmp/secret_content.yml
```

**Verify:**

```bash
# Confirm it is encrypted
head -1 /home/vagrant/exam/secret.yml
# Output: $ANSIBLE_VAULT;1.1;AES256

# Confirm content decrypts correctly
ansible-vault view /home/vagrant/exam/secret.yml \
  --vault-password-file /home/vagrant/exam/vault_key
```

> **Note:** The `ansible.cfg` for this exam does NOT set `vault_password_file`, so `--vault-password-file` must be passed on the command line when running playbooks that use the vault file.

---

## Task 6: Create Users Using Vault Variables

**Points: 20**

File: `/home/vagrant/exam/users.yml`

```yaml
---
- name: Create devadmin on dbservers group nodes
  hosts: dbservers
  vars_files:
    - secret.yml

  tasks:
    - name: Create devadmin with hashed password
      ansible.builtin.user:
        name: devadmin
        password: "{{ dev_pw | password_hash('sha512') }}"
        shell: /bin/bash
        state: present

- name: Create prodadmin on webservers group nodes
  hosts: webservers
  vars_files:
    - secret.yml

  tasks:
    - name: Create prodadmin with hashed password
      ansible.builtin.user:
        name: prodadmin
        password: "{{ prod_pw | password_hash('sha512') }}"
        shell: /bin/bash
        state: present
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook users.yml \
  --vault-password-file /home/vagrant/exam/vault_key
```

**Verify:**

```bash
ansible node3.lab.local -m ansible.builtin.command -a "id devadmin"
ansible node1.lab.local -m ansible.builtin.command -a "id prodadmin"
ansible node3.lab.local -m ansible.builtin.command \
  -a "getent passwd devadmin | cut -d: -f7"
# Output: /bin/bash
```

---

## Task 7: Create a Jinja2 Template for SSH Banner

**Points: 15**

### Step 1 — Create the template

File: `/home/vagrant/exam/templates/motd.j2`

```jinja2
Welcome to {{ ansible_fqdn }}
OS: {{ ansible_distribution }} {{ ansible_distribution_version }}
IPv4: {{ ansible_default_ipv4.address }}
```

### Step 2 — Create the playbook

File: `/home/vagrant/exam/sshd_banner.yml`

```yaml
---
- name: Deploy SSH banner using Jinja2 template
  hosts: lab

  tasks:
    - name: Deploy /etc/motd from template
      ansible.builtin.template:
        src: templates/motd.j2
        dest: /etc/motd
        owner: root
        group: root
        mode: '0644'
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook sshd_banner.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command -a "cat /etc/motd"
# Contains: Welcome to node1.lab.local, AlmaLinux, and the IP address
```

---

## Task 8: Configure Apache Web Server

**Points: 20**

### Step 1 — Create the index.html template

File: `/home/vagrant/exam/templates/index.html.j2`

```jinja2
Welcome to {{ ansible_fqdn }} ({{ ansible_default_ipv4.address }})
```

### Step 2 — Create the playbook

File: `/home/vagrant/exam/apache.yml`

```yaml
---
- name: Configure Apache web server on webservers group
  hosts: webservers

  tasks:
    - name: Install httpd (if not already installed)
      ansible.builtin.dnf:
        name: httpd
        state: present

    - name: Deploy index.html from template
      ansible.builtin.template:
        src: templates/index.html.j2
        dest: /var/www/html/index.html
        owner: root
        group: root
        mode: '0644'
      notify: restart httpd

    - name: Ensure httpd is started and enabled
      ansible.builtin.service:
        name: httpd
        state: started
        enabled: true

    - name: Ensure firewalld is running
      ansible.builtin.service:
        name: firewalld
        state: started
        enabled: true

    - name: Open http service in firewall
      ansible.posix.firewalld:
        service: http
        permanent: true
        state: enabled
        immediate: true

  handlers:
    - name: restart httpd
      ansible.builtin.service:
        name: httpd
        state: restarted
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook apache.yml
```

> **Note:** The `ansible.posix` collection must be installed. Install it with: `ansible-galaxy collection install ansible.posix -p /home/vagrant/exam/collections`

---

## Task 9: Generate /etc/hosts with Ansible Facts

**Points: 15**

### Step 1 — Create the myhosts template

File: `/home/vagrant/exam/templates/myhosts.j2`

```jinja2
# Managed by Ansible
{% for host in groups['lab'] %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }} {{ hostvars[host]['ansible_fqdn'] }} {{ hostvars[host]['ansible_hostname'] }}
{% endfor %}
```

### Step 2 — Create the playbook

File: `/home/vagrant/exam/hosts_file.yml`

```yaml
---
- name: Gather facts from all managed nodes
  hosts: lab
  gather_facts: true

- name: Deploy /etc/myhosts to all managed nodes
  hosts: lab

  tasks:
    - name: Deploy /etc/myhosts from template
      ansible.builtin.template:
        src: templates/myhosts.j2
        dest: /etc/myhosts
        owner: root
        group: root
        mode: '0644'
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook hosts_file.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command -a "cat /etc/myhosts"
# Should show all 5 lab group nodes with their IPs and FQDNs
```

> **Key point:** The two-play structure is important. The first play runs on all `lab` group nodes and gathers facts (this populates `hostvars` for every host). The second play then uses the template, which references `hostvars[host]` to build the complete list. If you skip the fact-gathering play, `hostvars` entries for other hosts will be empty.

---

## Task 10: Schedule a Cron Job

**Points: 10**

File: `/home/vagrant/exam/cron.yml`

```yaml
---
- name: Create cron job for vagrant user on all managed nodes
  hosts: lab

  tasks:
    - name: Schedule ansible_check cron job (every 15 minutes)
      ansible.builtin.cron:
        name: ansible_check
        user: vagrant
        minute: "*/15"
        hour: "*"
        day: "*"
        month: "*"
        weekday: "*"
        job: 'logger "Ansible managed cron"'
        state: present
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook cron.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command \
  -a "crontab -l" \
  --become-user vagrant --become
# Output includes: */15 * * * * logger "Ansible managed cron"
```

---

## Task 11: Create LVM Logical Volume

**Points: 20**

File: `/home/vagrant/exam/lvm.yml`

```yaml
---
- name: Configure LVM storage on dbservers group
  hosts: dbservers

  tasks:
    - name: Install lvm2 package
      ansible.builtin.dnf:
        name: lvm2
        state: present

    - name: Create volume group vg_data on /dev/loop0
      community.general.lvg:
        vg: vg_data
        pvs: /dev/loop0
        state: present

    - name: Create logical volume lv_data (500MB) in vg_data
      community.general.lvol:
        vg: vg_data
        lv: lv_data
        size: 500m
        state: present

    - name: Create ext4 filesystem on lv_data
      ansible.builtin.filesystem:
        fstype: ext4
        dev: /dev/vg_data/lv_data

    - name: Create /mnt/data mount point
      ansible.builtin.file:
        path: /mnt/data
        state: directory
        mode: '0755'

    - name: Mount /dev/vg_data/lv_data at /mnt/data (with fstab entry)
      ansible.posix.mount:
        path: /mnt/data
        src: /dev/vg_data/lv_data
        fstype: ext4
        opts: defaults
        state: mounted
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook lvm.yml
```

**Verify:**

```bash
ansible node3.lab.local -m ansible.builtin.command -a "vgs"
ansible node3.lab.local -m ansible.builtin.command -a "lvs vg_data"
ansible node3.lab.local -m ansible.builtin.command -a "findmnt /mnt/data"
```

> **Note:** `community.general` must be installed. The `ansible.posix.mount` module with `state: mounted` both mounts the filesystem immediately and creates a persistent `/etc/fstab` entry.

---

## Task 12: Configure SELinux

**Points: 15**

File: `/home/vagrant/exam/selinux.yml`

```yaml
---
- name: Ensure SELinux is in enforcing mode on all managed nodes
  hosts: lab

  tasks:
    - name: Ensure SELinux is in enforcing mode
      ansible.posix.selinux:
        policy: targeted
        state: enforcing

- name: Set httpd_can_network_connect SELinux boolean on webservers group
  hosts: webservers

  tasks:
    - name: Enable httpd_can_network_connect boolean (persistent)
      ansible.posix.seboolean:
        name: httpd_can_network_connect
        state: true
        persistent: true
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook selinux.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command -a "getenforce"
# Output: Enforcing

ansible node1.lab.local -m ansible.builtin.command \
  -a "getsebool httpd_can_network_connect"
# Output: httpd_can_network_connect --> on

ansible node3.lab.local -m ansible.builtin.command -a "getenforce"
# Output: Enforcing
```

> **Note:** `ansible.posix.selinux` may require a reboot if SELinux mode is changing from disabled to enforcing. In the lab environment it is assumed to already be permissive or enforcing, so no reboot is needed.

---

## Task 13: Create an Ansible Role

**Points: 25**

### Step 1 — Create the role structure

```bash
mkdir -p /home/vagrant/exam/roles/sample_apache/{tasks,handlers,templates,defaults,vars,files,meta}
```

### Step 2 — Role tasks

File: `/home/vagrant/exam/roles/sample_apache/tasks/main.yml`

```yaml
---
- name: Install httpd
  ansible.builtin.dnf:
    name: httpd
    state: present

- name: Deploy index.html from template
  ansible.builtin.template:
    src: index.html.j2
    dest: /var/www/html/index.html
    owner: root
    group: root
    mode: '0644'
  notify: restart httpd

- name: Start and enable httpd
  ansible.builtin.service:
    name: httpd
    state: started
    enabled: true
```

### Step 3 — Role handlers

File: `/home/vagrant/exam/roles/sample_apache/handlers/main.yml`

```yaml
---
- name: restart httpd
  ansible.builtin.service:
    name: httpd
    state: restarted
```

### Step 4 — Role template

File: `/home/vagrant/exam/roles/sample_apache/templates/index.html.j2`

```jinja2
Role deployed on {{ ansible_fqdn }}
```

### Step 5 — Role defaults (optional but good practice)

File: `/home/vagrant/exam/roles/sample_apache/defaults/main.yml`

```yaml
---
# sample_apache role defaults
apache_port: 80
```

### Step 6 — Create the playbook

File: `/home/vagrant/exam/role_test.yml`

```yaml
---
- name: Apply sample_apache role to node5
  hosts: node5.lab.local
  roles:
    - sample_apache
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook role_test.yml
```

**Verify:**

```bash
ansible node5.lab.local -m ansible.builtin.command -a "systemctl is-active httpd"
# Output: active

ansible node5.lab.local -m ansible.builtin.command \
  -a "cat /var/www/html/index.html"
# Output: Role deployed on node5.lab.local
```

---

## Task 14: Install Roles from Galaxy/Requirements

**Points: 10**

### Step 1 — Create the requirements file

File: `/home/vagrant/exam/roles/requirements.yml`

```yaml
---
roles:
  - name: geerlingguy.firewall
```

### Step 2 — Install the role

```bash
cd /home/vagrant/exam
ansible-galaxy install -r roles/requirements.yml
```

> **Note:** By default, `ansible-galaxy install` places roles in `~/.ansible/roles/`. The exam check looks in both `~/.ansible/roles/` and `/home/vagrant/exam/roles/`. To install into the project roles directory, add `-p /home/vagrant/exam/roles`:
>
> ```bash
> ansible-galaxy install -r roles/requirements.yml -p /home/vagrant/exam/roles
> ```

### Step 3 — Create the firewall playbook

File: `/home/vagrant/exam/firewall.yml`

```yaml
---
- name: Configure firewall on webservers group using geerlingguy.firewall role
  hosts: webservers
  vars:
    firewall_allowed_tcp_ports:
      - "80"
      - "443"
  roles:
    - geerlingguy.firewall
```

> **Note:** The `geerlingguy.firewall` role uses `firewall_allowed_tcp_ports` to open ports. Check the role's README after installing for exact variable names: `ansible-galaxy info geerlingguy.firewall`.

---

## Task 15: Use Conditionals and Loops

**Points: 15**

File: `/home/vagrant/exam/conditional.yml`

```yaml
---
- name: Configure server roles and install common packages
  hosts: lab

  vars:
    common_packages:
      - vim-enhanced
      - tree
      - wget

  tasks:
    - name: Write server_role file for webservers hosts (webserver)
      ansible.builtin.copy:
        content: "webserver\n"
        dest: /etc/server_role
        owner: root
        group: root
        mode: '0644'
      when: "'webservers' in group_names"

    - name: Write server_role file for dbservers hosts (dbserver)
      ansible.builtin.copy:
        content: "dbserver\n"
        dest: /etc/server_role
        owner: root
        group: root
        mode: '0644'
      when: "'dbservers' in group_names"

    - name: Write server_role file for balancers hosts (loadbalancer)
      ansible.builtin.copy:
        content: "loadbalancer\n"
        dest: /etc/server_role
        owner: root
        group: root
        mode: '0644'
      when: "'balancers' in group_names"

    - name: Install common packages on all managed nodes using loop
      ansible.builtin.dnf:
        name: "{{ item }}"
        state: present
      loop: "{{ common_packages }}"
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook conditional.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command -a "cat /etc/server_role"
# Output: webserver

ansible node3.lab.local -m ansible.builtin.command -a "cat /etc/server_role"
# Output: dbserver

ansible node5.lab.local -m ansible.builtin.command -a "cat /etc/server_role"
# Output: loadbalancer
```

---

## Task 16: Manage File Content with lineinfile/blockinfile

**Points: 10**

File: `/home/vagrant/exam/filecontent.yml`

```yaml
---
- name: Manage /etc/profile content on all managed nodes
  hosts: lab

  tasks:
    - name: Ensure HISTSIZE=5000 is in /etc/profile (lineinfile)
      ansible.builtin.lineinfile:
        path: /etc/profile
        line: "HISTSIZE=5000"
        regexp: "^HISTSIZE="
        state: present
        backup: yes

    - name: Add custom environment block to /etc/profile (blockinfile)
      ansible.builtin.blockinfile:
        path: /etc/profile
        marker: "# {mark} ANSIBLE MANAGED BLOCK — Custom environment"
        block: |
          # Custom environment
          export EDITOR=vim
          export LANG=en_US.UTF-8
        state: present
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook filecontent.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command -a "grep HISTSIZE /etc/profile"
# Output: HISTSIZE=5000

ansible node1.lab.local -m ansible.builtin.command -a "grep EDITOR /etc/profile"
# Output: export EDITOR=vim

ansible node1.lab.local -m ansible.builtin.command -a "grep LANG /etc/profile"
# Output: export LANG=en_US.UTF-8
```

> **Key points:**
> - `lineinfile` with `regexp:` ensures only one `HISTSIZE=` line exists (replaces existing or adds new).
> - `blockinfile` wraps the block in `# BEGIN ANSIBLE MANAGED BLOCK` / `# END ANSIBLE MANAGED BLOCK` markers, making it idempotent on re-runs.
> - The `backup: yes` on `lineinfile` creates a timestamped backup before modifying.

---

## Task 17: Create Custom Ansible Facts

**Points: 15**

File: `/home/vagrant/exam/custom_facts.yml`

```yaml
---
- name: Deploy custom Ansible facts to all managed nodes
  hosts: lab

  tasks:
    - name: Create /etc/ansible/facts.d directory
      ansible.builtin.file:
        path: /etc/ansible/facts.d
        state: directory
        owner: root
        group: root
        mode: '0755'

    - name: Deploy exam.fact custom fact file
      ansible.builtin.copy:
        content: |
          [general]
          project_name=ansible_lab
          role=managed_node
        dest: /etc/ansible/facts.d/exam.fact
        owner: root
        group: root
        mode: '0644'

    - name: Re-gather facts to pick up new custom facts
      ansible.builtin.setup:

    - name: Display custom fact project_name
      ansible.builtin.debug:
        msg: "Custom fact project_name = {{ ansible_local.exam.general.project_name }}"
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook custom_facts.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.setup \
  -a "filter=ansible_local"
# Output shows: "exam": { "general": { "project_name": "ansible_lab", "role": "managed_node" } }

ansible node1.lab.local -m ansible.builtin.command \
  -a "cat /etc/ansible/facts.d/exam.fact"
```

> **Key points:**
> - Custom fact files must be in `/etc/ansible/facts.d/` and have the `.fact` extension.
> - INI-format `.fact` files are automatically parsed by Ansible's setup module.
> - `ansible.builtin.setup` (called explicitly mid-play) re-reads facts so `ansible_local` is populated for the `debug` task in the same play run.

---

## Task 18: Create a System Report Playbook

**Points: 25**

### Step 1 — Create the report template

File: `/home/vagrant/exam/templates/report.j2`

```jinja2
=====================================
System Report — {{ ansible_date_time.date }}
=====================================
Hostname:     {{ ansible_fqdn }}
IP Address:   {{ ansible_default_ipv4.address }}
Total Memory: {{ ansible_memtotal_mb }} MB
CPU Count:    {{ ansible_processor_vcpus }}
OS:           {{ ansible_distribution }} {{ ansible_distribution_version }}
httpd:        {{ 'installed' if httpd_installed.rc == 0 else 'not installed' }}
=====================================
```

### Step 2 — Create the playbook

File: `/home/vagrant/exam/report.yml`

```yaml
---
- name: Generate system report on all managed nodes
  hosts: lab

  tasks:
    - name: Check if httpd is installed
      ansible.builtin.command:
        cmd: rpm -q httpd
      register: httpd_installed
      changed_when: false
      failed_when: false

    - name: Deploy system report from template
      ansible.builtin.template:
        src: templates/report.j2
        dest: /root/system_report.txt
        owner: root
        group: root
        mode: '0600'
```

**Run:**

```bash
cd /home/vagrant/exam
ansible-playbook report.yml
```

**Verify:**

```bash
ansible node1.lab.local -m ansible.builtin.command \
  -a "cat /root/system_report.txt"

ansible node3.lab.local -m ansible.builtin.command \
  -a "cat /root/system_report.txt"
```

**Sample output on node1:**

```
=====================================
System Report — 2026-02-19
=====================================
Hostname:     node1.lab.local
IP Address:   192.168.56.20
Total Memory: 512 MB
CPU Count:    1
OS:           AlmaLinux 9.4
httpd:        installed
=====================================
```

> **Key points:**
> - `failed_when: false` prevents the `rpm -q httpd` check from failing the playbook when httpd is not installed (rpm returns exit code 1 when a package is absent).
> - `changed_when: false` marks the check as never changed so it doesn't produce change output.
> - `register: httpd_installed` captures the result; `.rc` is the return code (0 = installed, 1 = not installed).
> - The template uses a Jinja2 inline conditional: `{{ 'installed' if httpd_installed.rc == 0 else 'not installed' }}`.
> - `ansible_processor_vcpus` gives the number of virtual CPUs; alternatively `ansible_processor_count` or `ansible_processor_nproc` can be used.
