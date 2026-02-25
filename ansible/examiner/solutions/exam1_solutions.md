# Practice Exam 1 - Reference Solutions

Working directory: `/home/vagrant/exam`

> **Note:** The exam checks in `exam1.yml` reference `/home/vagrant/exam/` paths. These solutions
> use `/home/vagrant/exam/` as the working directory per the exam instructions. Adjust paths to match
> whichever directory your lab environment actually uses.

---

## Task 1 - Install and Configure Ansible

**Points: 20**

Create the Ansible configuration file and inventory. Run these steps on the control node.

```bash
# Install Ansible if not already installed
sudo dnf install -y ansible-core

# Create the working directory
mkdir -p /home/vagrant/exam/roles
mkdir -p /home/vagrant/exam/collections
```

### `/home/vagrant/exam/ansible.cfg`

```ini
[defaults]
inventory         = /home/vagrant/exam/inventory
roles_path        = /home/vagrant/exam/roles
collections_paths = /home/vagrant/exam/collections
remote_user       = vagrant
host_key_checking = False
become            = True

[privilege_escalation]
become        = True
become_method = sudo
become_user   = root
become_ask_pass = False
```

### `/home/vagrant/exam/inventory`

```ini
[dev]
node1

[test]
node2

[prod]
node3
node4

[balancers]
node5

[webservers:children]
prod
```

**Verification:**

```bash
cd /home/vagrant/exam
ansible all --list-hosts
ansible webservers --list-hosts   # should show node3 and node4
ansible balancers --list-hosts    # should show node5
```

---

## Task 2 - Create Ad-Hoc Repository Playbook

**Points: 15**

### `/home/vagrant/exam/repos.yml`

```yaml
---
- name: Configure YUM repositories on all managed nodes
  hosts: all
  become: true

  tasks:
    - name: Configure BaseOS repository
      ansible.builtin.yum_repository:
        name: baseos
        description: BaseOS Repo
        baseurl: https://repo.almalinux.org/almalinux/9/BaseOS/aarch64/os/
        gpgcheck: true
        gpgkey: https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-9
        enabled: true

    - name: Configure AppStream repository
      ansible.builtin.yum_repository:
        name: appstream
        description: AppStream Repo
        baseurl: https://repo.almalinux.org/almalinux/9/AppStream/aarch64/os/
        gpgcheck: true
        gpgkey: https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-9
        enabled: true
```

**Run it:**

```bash
cd /home/vagrant/exam
ansible-playbook repos.yml
```

**Note:** The `baseurl` uses `aarch64` as shown in the exam spec. If your lab nodes run `x86_64`,
change the architecture accordingly.

---

## Task 3 - Install Ansible Collections

**Points: 15**

Collections must be installed into `/home/vagrant/exam/collections` so they are picked up by
`ansible.cfg`.

```bash
cd /home/vagrant/exam

ansible-galaxy collection install ansible.posix \
    -p /home/vagrant/exam/collections

ansible-galaxy collection install fedora.linux_system_roles \
    -p /home/vagrant/exam/collections
```

Alternatively, create a `collections/requirements.yml` and install from it:

### `/home/vagrant/exam/collections/requirements.yml`

```yaml
---
collections:
  - name: ansible.posix
  - name: fedora.linux_system_roles
```

```bash
ansible-galaxy collection install \
    -r /home/vagrant/exam/collections/requirements.yml \
    -p /home/vagrant/exam/collections
```

**Verification:**

```bash
ls /home/vagrant/exam/collections/ansible_collections/ansible/posix
ls /home/vagrant/exam/collections/ansible_collections/fedora/linux_system_roles
```

---

## Task 4 - Install Roles from Ansible Galaxy

**Points: 15**

### `/home/vagrant/exam/roles/requirements.yml`

```yaml
---
roles:
  - name: balancer
    src: geerlingguy.haproxy

  - name: phpinfo
    src: geerlingguy.php
```

**Install the roles:**

```bash
ansible-galaxy role install \
    -r /home/vagrant/exam/roles/requirements.yml \
    -p /home/vagrant/exam/roles
```

**Verification:**

```bash
ls /home/vagrant/exam/roles/balancer
ls /home/vagrant/exam/roles/phpinfo
```

---

## Task 5 - Create Apache Role

**Points: 30**

Create the role directory structure:

```bash
mkdir -p /home/vagrant/exam/roles/apache/{tasks,templates,handlers}
```

### `/home/vagrant/exam/roles/apache/tasks/main.yml`

```yaml
---
- name: Install httpd package (latest)
  ansible.builtin.dnf:
    name: httpd
    state: latest

- name: Start and enable httpd service
  ansible.builtin.service:
    name: httpd
    state: started
    enabled: true

- name: Allow http service through firewall
  ansible.posix.firewalld:
    service: http
    permanent: true
    state: enabled
    immediate: true

- name: Deploy index.html from template
  ansible.builtin.template:
    src: index.html.j2
    dest: /var/www/html/index.html
    owner: root
    group: root
    mode: '0644'
```

### `/home/vagrant/exam/roles/apache/templates/index.html.j2`

```jinja2
Welcome to {{ ansible_fqdn }} on {{ ansible_default_ipv4.address }}
```

### `/home/vagrant/exam/roles/apache/handlers/main.yml`

```yaml
---
- name: Restart httpd
  ansible.builtin.service:
    name: httpd
    state: restarted
```

### `/home/vagrant/exam/roles/apache/meta/main.yml`

```yaml
---
galaxy_info:
  author: student
  description: Apache web server role
  min_ansible_version: "2.9"
dependencies: []
```

**Note:** The `ansible.posix.firewalld` module requires the `ansible.posix` collection installed in
Task 3. Ensure `firewalld` is installed and running on the target nodes.

---

## Task 6 - Use Roles Playbook

**Points: 20**

### `/home/vagrant/exam/roles.yml`

```yaml
---
- name: Apply phpinfo role to webservers
  hosts: webservers
  become: true
  roles:
    - phpinfo

- name: Apply balancer role to balancers
  hosts: balancers
  become: true
  roles:
    - balancer
```

**Syntax check:**

```bash
cd /home/vagrant/exam
ansible-playbook roles.yml --syntax-check
```

---

## Task 7 - Install Packages

**Points: 20**

### `/home/vagrant/exam/packages.yml`

```yaml
---
- name: Install php and mariadb-server on dev, test, and prod
  hosts: dev,test,prod
  become: true

  tasks:
    - name: Install php and mariadb-server packages
      ansible.builtin.dnf:
        name:
          - php
          - mariadb-server
        state: present

- name: Install RPM Development Tools and update packages on dev
  hosts: dev
  become: true

  tasks:
    - name: Install RPM Development Tools package group
      ansible.builtin.dnf:
        name: "@RPM Development Tools"
        state: present

    - name: Update all packages to latest version
      ansible.builtin.dnf:
        name: "*"
        state: latest
```

**Syntax check:**

```bash
cd /home/vagrant/exam
ansible-playbook packages.yml --syntax-check
```

---

## Task 8 - Use timesync System Role

**Points: 15**

### `/home/vagrant/exam/timesync.yml`

```yaml
---
- name: Configure time synchronization using timesync system role
  hosts: all
  become: true

  vars:
    timesync_ntp_servers:
      - hostname: pool.ntp.org
        iburst: true

  roles:
    - fedora.linux_system_roles.timesync
```

**Syntax check:**

```bash
cd /home/vagrant/exam
ansible-playbook timesync.yml --syntax-check
```

**Note:** The `fedora.linux_system_roles.timesync` role configures `chrony` on RHEL/AlmaLinux 9.
After running the playbook, verify with:

```bash
# On a managed node:
grep pool.ntp.org /etc/chrony.conf
```

---

## Task 9 - Web Content Directory

**Points: 20**

### `/home/vagrant/exam/webcontent.yml`

```yaml
---
- name: Configure web content directory on dev hosts
  hosts: dev
  become: true

  tasks:
    - name: Ensure webdev group exists
      ansible.builtin.group:
        name: webdev
        state: present

    - name: Create /webdev directory with correct ownership and permissions
      ansible.builtin.file:
        path: /webdev
        state: directory
        group: webdev
        mode: '2775'

    - name: Set SELinux context on /webdev
      community.general.sefcontext:
        target: '/webdev(/.*)?'
        setype: httpd_sys_content_t
        state: present
      notify: Restore SELinux context

    - name: Apply SELinux context immediately
      ansible.builtin.command:
        cmd: restorecon -Rv /webdev
      changed_when: false

    - name: Create symbolic link /var/www/html/webdev -> /webdev
      ansible.builtin.file:
        src: /webdev
        dest: /var/www/html/webdev
        state: link

    - name: Create /webdev/index.html with content Development
      ansible.builtin.copy:
        content: "Development\n"
        dest: /webdev/index.html
        group: webdev
        mode: '0664'

  handlers:
    - name: Restore SELinux context
      ansible.builtin.command:
        cmd: restorecon -Rv /webdev
      changed_when: false
```

**Alternative approach using `ansible.posix.sefcontext`** (if `community.general` is not available):

```yaml
    - name: Set SELinux context on /webdev
      ansible.posix.sefcontext:
        target: '/webdev(/.*)?'
        setype: httpd_sys_content_t
        state: present

    - name: Apply SELinux context
      ansible.builtin.command:
        cmd: restorecon -Rv /webdev
      changed_when: false
```

**Verification on node1:**

```bash
stat -c '%a %G' /webdev           # should show: 2775 webdev
ls -la /var/www/html/webdev       # should show symlink
cat /webdev/index.html            # should show: Development
ls -Z /webdev                     # should show: httpd_sys_content_t
```

---

## Task 10 - Generate Hardware Report

**Points: 20**

### `/home/vagrant/exam/hwreport.yml`

```yaml
---
- name: Generate hardware report on all managed nodes
  hosts: all
  become: true

  tasks:
    - name: Write hardware report to /root/hwreport.txt
      ansible.builtin.copy:
        dest: /root/hwreport.txt
        content: |
          HOSTNAME={{ inventory_hostname }}
          MEMORY={{ ansible_memtotal_mb }}
          BIOS={{ ansible_bios_version | default('NONE') }}
          DISK_SIZE_VDA={{ ansible_devices.vda.size | default('NONE') }}
          DISK_SIZE_VDB={{ ansible_devices.vdb.size | default('NONE') }}
        owner: root
        group: root
        mode: '0600'
```

**Note:** The `ansible_devices` fact is a dictionary keyed by device name. If a device does not
exist the `default('NONE')` filter ensures the value is `NONE` rather than causing a task failure.
The `ansible_bios_version` fact may be `NA` in virtual machines; using `default('NONE')` handles
cases where the fact is undefined.

**Verification on node1:**

```bash
sudo cat /root/hwreport.txt
```

---

## Task 11 - Modify /etc/issue

**Points: 15**

### `/home/vagrant/exam/issue.yml`

```yaml
---
- name: Set /etc/issue content on dev hosts
  hosts: dev
  become: true

  tasks:
    - name: Set /etc/issue to Development
      ansible.builtin.copy:
        content: "Development\n"
        dest: /etc/issue

- name: Set /etc/issue content on test hosts
  hosts: test
  become: true

  tasks:
    - name: Set /etc/issue to Test
      ansible.builtin.copy:
        content: "Test\n"
        dest: /etc/issue

- name: Set /etc/issue content on prod hosts
  hosts: prod
  become: true

  tasks:
    - name: Set /etc/issue to Production
      ansible.builtin.copy:
        content: "Production\n"
        dest: /etc/issue
```

**Alternative single-play approach using conditionals:**

```yaml
---
- name: Modify /etc/issue based on host group
  hosts: all
  become: true

  tasks:
    - name: Set /etc/issue for dev hosts
      ansible.builtin.copy:
        content: "Development\n"
        dest: /etc/issue
      when: "'dev' in group_names"

    - name: Set /etc/issue for test hosts
      ansible.builtin.copy:
        content: "Test\n"
        dest: /etc/issue
      when: "'test' in group_names"

    - name: Set /etc/issue for prod hosts
      ansible.builtin.copy:
        content: "Production\n"
        dest: /etc/issue
      when: "'prod' in group_names"
```

---

## Task 12 - Generate /etc/hosts File

**Points: 20**

### `/home/vagrant/exam/hosts.j2`

```jinja2
127.0.0.1   localhost localhost.localdomain
::1         localhost localhost.localdomain
{% for host in groups['all'] %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }} {{ hostvars[host]['ansible_fqdn'] }} {{ hostvars[host]['ansible_hostname'] }}
{% endfor %}
```

**Note:** This template iterates over `groups['all']` and uses facts gathered from each host.
The playbook must gather facts from all hosts before the template is applied, which is why we
use a two-play structure.

### `/home/vagrant/exam/hosts.yml`

```yaml
---
- name: Gather facts from all hosts
  hosts: all
  become: true

- name: Deploy /etc/myhosts from template on dev hosts
  hosts: dev
  become: true

  tasks:
    - name: Generate /etc/myhosts from hosts.j2 template
      ansible.builtin.template:
        src: /home/vagrant/exam/hosts.j2
        dest: /etc/myhosts
        owner: root
        group: root
        mode: '0644'
```

**Verification on node1:**

```bash
cat /etc/myhosts
# Should contain entries for all managed hosts
```

---

## Task 13 - Create Password Vault

**Points: 15**

```bash
# Store the vault password in a file
echo 'sunshine42day' > /home/vagrant/exam/vault_key
chmod 600 /home/vagrant/exam/vault_key

# Create the encrypted vault file
ansible-vault create /home/vagrant/exam/credentials.yml \
    --vault-password-file /home/vagrant/exam/vault_key
```

When the editor opens, enter the following content:

```yaml
---
dev_pw: devSec#42
mgr_pw: mgrSec#42
```

Save and exit the editor (`:wq` in vi).

**Alternatively, create the file first then encrypt it:**

```bash
cat > /tmp/locker_plain.yml << 'EOF'
---
dev_pw: devSec#42
mgr_pw: mgrSec#42
EOF

ansible-vault encrypt /tmp/locker_plain.yml \
    --vault-password-file /home/vagrant/exam/vault_key \
    --output /home/vagrant/exam/credentials.yml

rm /tmp/locker_plain.yml
```

**Verification:**

```bash
# Confirm it is encrypted
head -1 /home/vagrant/exam/credentials.yml    # should show $ANSIBLE_VAULT;...

# Decrypt and view contents
ansible-vault view /home/vagrant/exam/credentials.yml \
    --vault-password-file /home/vagrant/exam/vault_key
```

---

## Task 14 - Create User Accounts

**Points: 20**

First, create a user list variable file. This file does not need to be encrypted.

### `/home/vagrant/exam/user_list.yml`

```yaml
---
users:
  - name: anna
    job: developer

  - name: tom
    job: developer

  - name: maria
    job: manager
```

### `/home/vagrant/exam/users.yml`

```yaml
---
- name: Create developer accounts on dev and test hosts
  hosts: dev,test
  become: true
  vars_files:
    - credentials.yml
    - user_list.yml

  tasks:
    - name: Ensure appdev group exists
      ansible.builtin.group:
        name: appdev
        state: present

    - name: Create developer user accounts
      ansible.builtin.user:
        name: "{{ item.name }}"
        groups: appdev
        append: true
        password: "{{ dev_pw | password_hash('sha512') }}"
        state: present
      loop: "{{ users | selectattr('job', 'equalto', 'developer') | list }}"

- name: Create manager accounts on prod hosts
  hosts: prod
  become: true
  vars_files:
    - credentials.yml
    - user_list.yml

  tasks:
    - name: Ensure appmgr group exists
      ansible.builtin.group:
        name: appmgr
        state: present

    - name: Create manager user accounts
      ansible.builtin.user:
        name: "{{ item.name }}"
        groups: appmgr
        append: true
        password: "{{ mgr_pw | password_hash('sha512') }}"
        state: present
      loop: "{{ users | selectattr('job', 'equalto', 'manager') | list }}"
```

**Run with the vault password file:**

```bash
cd /home/vagrant/exam
ansible-playbook users.yml \
    --vault-password-file /home/vagrant/exam/vault_key
```

**Syntax check** (vault password file is required even for syntax check when vault files are referenced):

```bash
ansible-playbook users.yml --syntax-check \
    --vault-password-file /home/vagrant/exam/vault_key
```

**Verification:**

```bash
# On node1 (dev):
getent group appdev
getent passwd anna

# On node3 (prod):
getent group appmgr
getent passwd maria
```

---

## Task 15 - Rekey Ansible Vault

**Points: 10**

The file `/home/vagrant/exam/payments.yml` is currently encrypted with `oldpass2024`.
Rekey it to use the new password `newpass2024`.

```bash
ansible-vault rekey /home/vagrant/exam/payments.yml \
    --ask-vault-pass
```

When prompted:
- **Vault password:** `oldpass2024`
- **New Vault password:** `newpass2024`
- **Confirm New Vault password:** `newpass2024`

**Non-interactive approach using password files:**

```bash
echo 'oldpass2024' > /tmp/old_pass.txt
echo 'newpass2024'   > /tmp/new_pass.txt

ansible-vault rekey /home/vagrant/exam/payments.yml \
    --vault-password-file /tmp/old_pass.txt \
    --new-vault-password-file /tmp/new_pass.txt

rm /tmp/old_pass.txt /tmp/new_pass.txt
```

**Verification:**

```bash
# Confirm it is still encrypted
head -1 /home/vagrant/exam/payments.yml   # should show $ANSIBLE_VAULT;...

# View with new password
ansible-vault view /home/vagrant/exam/payments.yml \
    --vault-password-file /tmp/new_pass.txt
```

---

## Task 16 - Configure Cron Job

**Points: 10**

### `/home/vagrant/exam/cron.yml`

```yaml
---
- name: Configure cron job on all managed nodes
  hosts: all
  become: true

  tasks:
    - name: Add cron job to log Ansible health check every 2 minutes
      ansible.builtin.cron:
        name: "system_health_check"
        minute: "*/2"
        hour: "*"
        day: "*"
        month: "*"
        weekday: "*"
        user: vagrant
        job: 'logger "Ansible health check"'
        state: present
```

**Verification on node1:**

```bash
# Check vagrant's crontab
crontab -u vagrant -l
# Should contain: */2 * * * * logger "Ansible health check"
```

**Note:** The `ansible.builtin.cron` module adds the job to the specified user's crontab.
The exam check runs `crontab -l` (without `-u vagrant`) as the vagrant user, so the job will
be found correctly.

---

## Task 17 - Create Logical Volume

**Points: 20**

### `/home/vagrant/exam/lvm.yml`

```yaml
---
- name: Create logical volume on all managed nodes
  hosts: all
  become: true

  tasks:
    - name: Handle logical volume creation with error handling
      block:
        - name: Fail with message if volume group storage_vg does not exist
          ansible.builtin.fail:
            msg: "Volume group does not exist"
          when: "'storage_vg' not in ansible_lvm.vgs"

        - name: Create logical volume app_lv (1500 MiB)
          community.general.lvol:
            vg: storage_vg
            lv: app_lv
            size: 1500m
          register: lv_result

        - name: Format logical volume with ext4
          community.general.filesystem:
            fstype: ext4
            dev: /dev/storage_vg/app_lv

      rescue:
        - name: Display message when 1500 MiB LV cannot be created
          ansible.builtin.debug:
            msg: "Could not create logical volume of that size"
          when: lv_result is defined and lv_result is failed

        - name: Display message when volume group does not exist
          ansible.builtin.debug:
            msg: "Volume group does not exist"
          when: "'storage_vg' not in ansible_lvm.vgs"

        - name: Create logical volume app_lv at fallback size 800 MiB
          community.general.lvol:
            vg: storage_vg
            lv: app_lv
            size: 800m
          when: "'storage_vg' in ansible_lvm.vgs"

        - name: Format fallback logical volume with ext4
          community.general.filesystem:
            fstype: ext4
            dev: /dev/storage_vg/app_lv
          when: "'storage_vg' in ansible_lvm.vgs"
```

**Alternative using `ansible.builtin.command` for broader compatibility:**

```yaml
---
- name: Create logical volume on all managed nodes
  hosts: all
  become: true

  tasks:
    - name: Check if volume group storage_vg exists
      ansible.builtin.command:
        cmd: vgs storage_vg
      register: vg_check
      failed_when: false
      changed_when: false

    - name: Report missing volume group
      ansible.builtin.debug:
        msg: "Volume group does not exist"
      when: vg_check.rc != 0

    - name: Create and format logical volume when VG exists
      when: vg_check.rc == 0
      block:
        - name: Attempt to create 1500 MiB logical volume
          community.general.lvol:
            vg: storage_vg
            lv: app_lv
            size: 1500m
          register: lv_primary

      rescue:
        - name: Report that 1500 MiB size is unavailable
          ansible.builtin.debug:
            msg: "Could not create logical volume of that size"

        - name: Create 800 MiB logical volume as fallback
          community.general.lvol:
            vg: storage_vg
            lv: app_lv
            size: 800m

    - name: Format logical volume with ext4
      community.general.filesystem:
        fstype: ext4
        dev: /dev/storage_vg/app_lv
      when: vg_check.rc == 0
```

**Verification:**

```bash
# On a node with the storage_vg VG:
sudo lvs storage_vg
sudo blkid /dev/storage_vg/app_lv   # should show TYPE="ext4"
```

---

## Summary Table

| Task | File(s) Created | Key Modules Used |
|------|----------------|------------------|
| 1 | `ansible.cfg`, `inventory` | Configuration files |
| 2 | `repos.yml` | `ansible.builtin.yum_repository` |
| 3 | `collections/` | `ansible-galaxy collection install` |
| 4 | `roles/requirements.yml` | `ansible-galaxy role install` |
| 5 | `roles/apache/` | `ansible.builtin.dnf`, `ansible.posix.firewalld`, `ansible.builtin.template` |
| 6 | `roles.yml` | Role references |
| 7 | `packages.yml` | `ansible.builtin.dnf` |
| 8 | `timesync.yml` | `fedora.linux_system_roles.timesync` |
| 9 | `webcontent.yml` | `ansible.builtin.file`, `ansible.posix.sefcontext`, `ansible.builtin.copy` |
| 10 | `hwreport.yml` | `ansible.builtin.copy` with facts |
| 11 | `issue.yml` | `ansible.builtin.copy` |
| 12 | `hosts.j2`, `hosts.yml` | `ansible.builtin.template` |
| 13 | `credentials.yml`, `vault_key` | `ansible-vault create` |
| 14 | `user_list.yml`, `users.yml` | `ansible.builtin.user`, `ansible.builtin.group` |
| 15 | (rekey `payments.yml`) | `ansible-vault rekey` |
| 16 | `cron.yml` | `ansible.builtin.cron` |
| 17 | `lvm.yml` | `community.general.lvol`, `community.general.filesystem` |

## Tips

- Always run `ansible-playbook --syntax-check` before executing a playbook.
- Use FQCNs (Fully Qualified Collection Names) for all modules, e.g. `ansible.builtin.dnf` not just `dnf`.
- The `become: true` setting in `ansible.cfg` applies globally, but it is good practice to set it in playbooks as well for clarity.
- For vault operations, always verify with `head -1 <file>` that the file starts with `$ANSIBLE_VAULT`.
- The `password_hash('sha512')` filter requires the `passlib` Python library on the control node (`pip install passlib`).
- Tasks in `rescue:` blocks run only when the corresponding `block:` raises an error. Use `when:` conditions in `rescue:` to handle multiple failure scenarios.
- The `ansible_lvm` fact requires LVM tools to be installed on managed nodes. If facts are unavailable, gather them explicitly with `ansible.builtin.setup`.
