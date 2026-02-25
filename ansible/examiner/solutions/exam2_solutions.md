# Practice Exam 2 - Reference Solutions

**Working directory:** `/home/vagrant/exam`
**Hosts:** control, node1 (dev), node2 (test), node3 (prod/webservers), node4 (balancers)
**Remote user:** vagrant
**Privilege escalation:** sudo

---

## Task 1: Install and Configure Ansible

**Points: 20**

Install ansible-core on the control node, then create the configuration file and inventory.

### Step 1 - Install ansible-core (run on control node as root/sudo)

```bash
sudo dnf install -y ansible-core
```

### Step 2 - Create the working directory

```bash
mkdir -p /home/vagrant/exam/roles
mkdir -p /home/vagrant/exam/collections
```

### `/home/vagrant/exam/ansible.cfg`

```ini
[defaults]
inventory       = /home/vagrant/exam/inventory
roles_path      = /home/vagrant/exam/roles
collections_path = /home/vagrant/exam/collections
remote_user     = vagrant
host_key_checking = False

[privilege_escalation]
become      = True
become_method = sudo
become_user   = root
become_ask_pass = False
```

### `/home/vagrant/exam/inventory`

```ini
[dev]
node1.lab.local

[test]
node2.lab.local

[prod]
node3.lab.local

[balancers]
node4.lab.local

[webservers:children]
prod
```

### Verify

```bash
ansible all -m ping
```

**Notes:**
- The `[webservers:children]` section makes `prod` a child group of `webservers`, so node3 is reachable via both `prod` and `webservers`.
- `host_key_checking = False` is set under `[defaults]`, not `[privilege_escalation]`.
- `collections_path` must point to the same directory you will install collections into (Task 3).

---

## Task 2: Configure Yum Repositories

**Points: 15**

### `/home/vagrant/exam/repos.yml`

```yaml
---
- name: Configure Yum Repositories on all managed nodes
  hosts: all
  become: true

  tasks:
    - name: Configure BaseOS repository
      ansible.builtin.yum_repository:
        name: baseos
        description: "BaseOS Repository"
        baseurl: https://repo.almalinux.org/almalinux/9/BaseOS/aarch64/os/
        gpgcheck: yes
        gpgkey: https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-9
        enabled: yes

    - name: Configure AppStream repository
      ansible.builtin.yum_repository:
        name: appstream
        description: "AppStream Repository"
        baseurl: https://repo.almalinux.org/almalinux/9/AppStream/aarch64/os/
        gpgcheck: yes
        gpgkey: https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux-9
        enabled: yes
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook repos.yml
```

**Notes:**
- The `yum_repository` module creates `.repo` files under `/etc/yum.repos.d/` named after the `name` parameter (e.g., `baseos.repo`, `appstream.repo`).
- Adjust the `baseurl` architecture (`aarch64` vs `x86_64`) to match your lab nodes if needed.
- `gpgcheck: yes` and `enabled: yes` accept boolean values; `1` or `true` also work.

---

## Task 3: Install Ansible Collections

**Points: 15**

### Steps

```bash
mkdir -p /home/vagrant/exam/collections

cd /home/vagrant/exam

ansible-galaxy collection install ansible.posix \
    -p /home/vagrant/exam/collections

ansible-galaxy collection install fedora.linux_system_roles \
    -p /home/vagrant/exam/collections
```

### Verify

```bash
ls /home/vagrant/exam/collections/ansible_collections/ansible/posix
ls /home/vagrant/exam/collections/ansible_collections/fedora/linux_system_roles
```

**Notes:**
- The `-p` flag sets the install path. Collections land under `<path>/ansible_collections/<namespace>/<collection>`.
- If your `ansible.cfg` has `collections_path = /home/vagrant/exam/collections`, you can omit `-p` for subsequent installs and Ansible will find them automatically.
- The `fedora.linux_system_roles` collection provides the `timesync` and `selinux` roles used in Tasks 7a and 7b.

---

## Task 4: Install Roles from a Requirements File

**Points: 15**

### `/home/vagrant/exam/roles/requirements.yml`

```yaml
---
- src: geerlingguy.haproxy
  name: balancer

- src: geerlingguy.php
  name: phpinfo
```

### Install

```bash
cd /home/vagrant/exam
ansible-galaxy install -r roles/requirements.yml -p roles
```

### Verify

```bash
ls /home/vagrant/exam/roles/balancer
ls /home/vagrant/exam/roles/phpinfo
```

**Notes:**
- The `name:` key renames the installed role. Without it, the role would be installed as `geerlingguy.haproxy`.
- The `-p roles` flag installs into the `roles/` subdirectory relative to your current working directory (`/home/vagrant/exam/roles`), which matches the `roles_path` in `ansible.cfg`.

---

## Task 5: Create an Apache Role

**Points: 25**

### Step 1 - Initialize the role skeleton

```bash
cd /home/vagrant/exam
ansible-galaxy init roles/apache
```

### `/home/vagrant/exam/roles/apache/tasks/main.yml`

```yaml
---
- name: Install httpd and firewalld packages
  ansible.builtin.dnf:
    name:
      - httpd
      - firewalld
    state: present

- name: Start and enable firewalld
  ansible.builtin.service:
    name: firewalld
    state: started
    enabled: true

- name: Start and enable httpd
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
    src: template.j2
    dest: /var/www/html/index.html
    owner: root
    group: root
    mode: '0644'
```

### `/home/vagrant/exam/roles/apache/templates/template.j2`

```
My host is {{ ansible_fqdn }} on {{ ansible_default_ipv4.address }}
```

### `/home/vagrant/exam/apache_role.yml`

```yaml
---
- name: Apply apache role to dev group
  hosts: dev
  become: true

  roles:
    - apache
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook apache_role.yml
```

**Notes:**
- `ansible.posix.firewalld` requires the `ansible.posix` collection (installed in Task 3).
- `immediate: true` applies the firewall rule to the running firewall without a reload. `permanent: true` persists it across reboots.
- Firewalld must be started before opening ports, so the service task comes before the firewalld task.
- The template uses `ansible_fqdn` and `ansible_default_ipv4.address`, which are gathered automatically by the setup module.

---

## Task 6: Use Multiple Roles in a Playbook

**Points: 20**

### `/home/vagrant/exam/roles.yml`

```yaml
---
- name: Apply apache role to webservers group
  hosts: webservers
  become: true

  roles:
    - apache

- name: Apply apache role to balancers group
  hosts: balancers
  become: true

  roles:
    - apache
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook roles.yml
```

### Verify

```bash
curl http://node3.lab.local/
curl http://node4.lab.local/
```

**Notes:**
- node3 is in `prod`, which is a child of `webservers` via `[webservers:children]` in the inventory. Using `hosts: webservers` targets node3.
- Both plays use the same `apache` role defined in Task 5.
- The order (webservers before balancers) is as specified in the task.

---

## Task 7a: Use the timesync System Role

**Points: 15**

### `/home/vagrant/exam/timesync.yml`

```yaml
---
- name: Configure NTP with timesync system role
  hosts: all
  become: true

  vars:
    timesync_ntp_servers:
      - hostname: pool.ntp.org
        iburst: yes

  roles:
    - fedora.linux_system_roles.timesync
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook timesync.yml
```

### Verify

```bash
ansible all -m command -a 'chronyc tracking'
ansible all -m command -a 'grep pool.ntp.org /etc/chrony.conf'
```

**Notes:**
- The role is referenced by its fully-qualified collection name: `fedora.linux_system_roles.timesync`.
- Alternatively, copy the roles out of the collection: `cp -r collections/ansible_collections/fedora/linux_system_roles/roles/* roles/` and then reference the role as simply `timesync`.
- `timesync_ntp_provider` defaults to `chrony` on RHEL/AlmaLinux 9, so it does not need to be set explicitly, but you can add `timesync_ntp_provider: chrony` to the vars block for clarity.
- The role configures `/etc/chrony.conf` and ensures `chronyd` is running and enabled.

---

## Task 7b: Use the SELinux System Role

**Points: 10**

### `/home/vagrant/exam/selinux.yml`

```yaml
---
- name: Configure SELinux enforcing mode with system role
  hosts: all
  become: true

  vars:
    selinux_state: enforcing

  roles:
    - fedora.linux_system_roles.selinux
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook selinux.yml
```

### Verify

```bash
ansible all -m command -a 'getenforce'
```

**Notes:**
- The SELinux role may reboot managed nodes if the current SELinux state differs from the target (e.g., changing from disabled requires a reboot). The role handles this with a reboot handler.
- `selinux_state: enforcing` sets both the runtime and persistent (`/etc/selinux/config`) configuration.
- If SELinux is already enforcing, the role makes no changes.

---

## Task 8: Install Packages in Multiple Groups

**Points: 18**

### `/home/vagrant/exam/packages.yml`

```yaml
---
- name: Install vsftpd and mariadb-server on dev and test
  hosts: dev,test
  become: true

  tasks:
    - name: Install vsftpd and mariadb-server
      ansible.builtin.dnf:
        name:
          - vsftpd
          - mariadb-server
        state: present

- name: Install RPM Development Tools on prod
  hosts: prod
  become: true

  tasks:
    - name: Install RPM Development Tools package group
      ansible.builtin.dnf:
        name: "@RPM Development Tools"
        state: present

- name: Update all packages on dev to latest
  hosts: dev
  become: true

  tasks:
    - name: Update all packages to latest
      ansible.builtin.dnf:
        name: "*"
        state: latest
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook packages.yml
```

**Notes:**
- Package groups use the `@GroupName` syntax with `ansible.builtin.dnf`. The `@` prefix tells DNF it is a group.
- `"@RPM Development Tools"` must be quoted because of the `@` character.
- Three separate plays are used as required by the task description.
- `state: latest` with `name: "*"` updates all installed packages.

---

## Task 9: Configure Web Content Directory

**Points: 22**

### `/home/vagrant/exam/webcontent.yml`

```yaml
---
- name: Configure web content directory on dev
  hosts: dev
  become: true

  tasks:
    - name: Create /devweb directory owned by vagrant group
      ansible.builtin.file:
        path: /devweb
        state: directory
        group: vagrant
        mode: '2775'

    - name: Set SELinux context type on /devweb
      community.general.sefcontext:
        target: '/devweb(/.*)?'
        setype: httpd_sys_content_t
        state: present
      notify: Restore SELinux context

    - name: Apply SELinux context immediately
      ansible.builtin.command:
        cmd: restorecon -Rv /devweb

    - name: Create /devweb/index.html with content Development
      ansible.builtin.copy:
        content: "Development\n"
        dest: /devweb/index.html
        mode: '0644'

    - name: Create symlink from /var/www/html/devweb to /devweb
      ansible.builtin.file:
        src: /devweb
        dest: /var/www/html/devweb
        state: link

  handlers:
    - name: Restore SELinux context
      ansible.builtin.command:
        cmd: restorecon -Rv /devweb
```

**Alternative approach using ansible.posix.sefcontext (if community.general is not available):**

```yaml
---
- name: Configure web content directory on dev
  hosts: dev
  become: true

  tasks:
    - name: Create /devweb directory owned by vagrant group
      ansible.builtin.file:
        path: /devweb
        state: directory
        group: vagrant
        mode: '2775'

    - name: Set SELinux file context for /devweb
      ansible.builtin.command:
        cmd: semanage fcontext -a -t httpd_sys_content_t "/devweb(/.*)?"
      ignore_errors: true

    - name: Apply SELinux file context
      ansible.builtin.command:
        cmd: restorecon -Rv /devweb

    - name: Create /devweb/index.html with content Development
      ansible.builtin.copy:
        content: "Development\n"
        dest: /devweb/index.html
        mode: '0644'

    - name: Create symlink from /var/www/html/devweb to /devweb
      ansible.builtin.file:
        src: /devweb
        dest: /var/www/html/devweb
        state: link
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook webcontent.yml
```

### Verify

```bash
curl http://node1.lab.local/devweb/
```

**Notes:**
- Mode `2775` sets the setgid bit (2) plus rwxrwxr-x permissions. This ensures files created in the directory inherit the group.
- The SELinux context `httpd_sys_content_t` is required for Apache to serve content from `/devweb`.
- `restorecon -Rv /devweb` applies the fcontext policy to existing files recursively.
- The symlink `state: link` uses `src` (the target of the link) and `dest` (where the link lives). This creates: `/var/www/html/devweb -> /devweb`.
- Apache must already be running on node1 (from Task 5) for `curl` to work.

---

## Task 10: Generate a Hardware Report

**Points: 18**

### `/home/vagrant/exam/hwreport.yml`

```yaml
---
- name: Generate hardware report on all managed nodes
  hosts: all
  become: true

  tasks:
    - name: Generate /root/hwreport.txt
      ansible.builtin.copy:
        content: |
          #hwreport
          HOSTNAME={{ ansible_hostname }}
          MEMORY={{ ansible_memtotal_mb }}
          BIOS={{ ansible_bios_version }}
          CPU={{ ansible_processor[2] | default('NONE') }}
          DISK_SIZE_SDA={{ ansible_devices['sda']['size'] | default('NONE') }}
        dest: /root/hwreport.txt
        owner: root
        group: root
        mode: '0644'
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook hwreport.yml
```

### Verify

```bash
ansible all -m command -a 'cat /root/hwreport.txt' --become
```

**Notes:**
- `ansible_processor` is a list. Index `[2]` typically contains the model name on x86_64 systems (index 0 is the socket count, 1 is the vendor). Use `| default('NONE')` in case the index does not exist.
- `ansible_devices['sda']['size']` will raise an error if `sda` does not exist. The `| default('NONE')` filter handles this gracefully.
- `ansible_bios_version` may be `NA` or similar on virtual machines - this is expected.
- All fact variables are populated by the implicit `gather_facts: true` (which is the default).

---

## Task 11: Replace /etc/issue by Host Group

**Points: 15**

### `/home/vagrant/exam/issue.yml`

```yaml
---
- name: Set /etc/issue content based on host group
  hosts: all
  become: true

  tasks:
    - name: Set /etc/issue to Development on dev hosts
      ansible.builtin.copy:
        content: "Development\n"
        dest: /etc/issue
      when: inventory_hostname in groups['dev']

    - name: Set /etc/issue to Test on test hosts
      ansible.builtin.copy:
        content: "Test\n"
        dest: /etc/issue
      when: inventory_hostname in groups['test']

    - name: Set /etc/issue to Production on prod hosts
      ansible.builtin.copy:
        content: "Production\n"
        dest: /etc/issue
      when: inventory_hostname in groups['prod']
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook issue.yml
```

### Verify

```bash
ansible all -m command -a 'cat /etc/issue'
```

**Notes:**
- `inventory_hostname in groups['dev']` evaluates to `true` when the current host is a member of the `dev` group. This is the idiomatic Ansible way to check group membership in a `when` condition.
- The `\n` at the end of each content string is good practice to ensure the file ends with a newline.
- Using three tasks (one per group) is cleaner and more explicit than using `elif` logic.

---

## Task 12: Generate /etc/myhosts with a Jinja2 Template

**Points: 18**

### `/home/vagrant/exam/myhosts.j2`

```jinja2
127.0.0.1 localhost.localdomain localhost
{% for host in groups['all'] %}
{{ hostvars[host]['ansible_default_ipv4']['address'] }} {{ hostvars[host]['ansible_fqdn'] }} {{ hostvars[host]['ansible_hostname'] }}
{% endfor %}
```

### `/home/vagrant/exam/hosts.yml`

```yaml
---
- name: Gather facts from all hosts
  hosts: all
  become: true

- name: Deploy /etc/myhosts to dev group
  hosts: dev
  become: true

  tasks:
    - name: Deploy myhosts template to /etc/myhosts
      ansible.builtin.template:
        src: myhosts.j2
        dest: /etc/myhosts
        owner: root
        group: root
        mode: '0644'
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook hosts.yml
```

### Verify

```bash
ansible dev -m command -a 'cat /etc/myhosts'
```

**Notes:**
- The first play (`hosts: all`) has no tasks. Its sole purpose is to trigger fact gathering on all nodes so that `hostvars` is populated for every host in the inventory.
- Without the first play, `hostvars[host]['ansible_default_ipv4']` would be undefined for hosts that are not in `dev`.
- `hostvars` is a special Ansible variable that contains the facts and variables for every host in the inventory.
- The `{% for %}` loop iterates over all hosts in the `all` group, generating one line per host.
- `{% for host in groups['all'] %}` does NOT include the control node because the control node is not in the inventory (only node1-node4 are managed nodes).

---

## Task 13: Use Ansible Vault

**Points: 15**

### Step 1 - Create the vault password file

```bash
echo 'grape$vine99' > /home/vagrant/exam/vault_key
chmod 600 /home/vagrant/exam/vault_key
```

### Step 2 - Create the encrypted vault file

```bash
cd /home/vagrant/exam
ansible-vault create encrypted_vars.yml --vault-password-file=vault_key
```

When the editor opens, enter:

```yaml
dev_pw: d3vKey!9
mgr_pw: m9rKey!9
```

Save and quit (`:wq` in vim).

### Verify

```bash
ansible-vault view encrypted_vars.yml --vault-password-file=vault_key
```

**Notes:**
- `ansible-vault create` opens `$EDITOR` (usually vim) for you to type the content. The file is encrypted on save.
- If you need to edit the file later: `ansible-vault edit encrypted_vars.yml --vault-password-file=vault_key`
- The encrypted file starts with `$ANSIBLE_VAULT;1.1;AES256` on the first line.
- `chmod 600` on `vault_key` is good practice to protect the password file.
- These variables (`dev_pw`, `mgr_pw`) are used in Task 14 as passwords for user creation.

---

## Task 14: Create Users Using Vault Variables

**Points: 22**

### `/home/vagrant/exam/user_list.yml`

```yaml
---
users:
  - name: tom
    uid: 2001
    job: developer
    password_expire_days: 30
  - name: lisa
    uid: 2002
    job: manager
    password_expire_days: 30
  - name: jake
    uid: 2003
    job: developer
    password_expire_days: 30
```

### `/home/vagrant/exam/users.yml`

```yaml
---
- name: Create groups and users on dev and test hosts
  hosts: dev,test
  become: true

  vars_files:
    - user_list.yml
    - encrypted_vars.yml

  tasks:
    - name: Create appdev group on dev and test hosts
      ansible.builtin.group:
        name: appdev
        state: present

    - name: Create appmgr group on test hosts only
      ansible.builtin.group:
        name: appmgr
        state: present
      when: inventory_hostname in groups['test']

    - name: Create developer users on dev and test hosts
      ansible.builtin.user:
        name: "{{ item.name }}"
        uid: "{{ item.uid }}"
        group: appdev
        password: "{{ dev_pw | password_hash('sha512') }}"
        state: present
      loop: "{{ users }}"
      when: item.job == 'developer'

    - name: Create manager users on test hosts only
      ansible.builtin.user:
        name: "{{ item.name }}"
        uid: "{{ item.uid }}"
        group: appmgr
        password: "{{ mgr_pw | password_hash('sha512') }}"
        state: present
      loop: "{{ users }}"
      when:
        - item.job == 'manager'
        - inventory_hostname in groups['test']
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook users.yml --vault-password-file=vault_key
```

### Verify

```bash
ansible dev -m command -a 'id tom'
ansible test -m command -a 'id lisa'
ansible dev -m command -a 'getent group appdev'
ansible test -m command -a 'getent group appmgr'
```

**Notes:**
- `vars_files` loads both files at play level. `encrypted_vars.yml` is decrypted transparently when `--vault-password-file` is provided on the command line.
- `password_hash('sha512')` is a Jinja2 filter that hashes the plaintext password into a format suitable for `/etc/shadow`. Using the plaintext password directly would store it unhashed.
- The `when` condition on the manager task uses a list (AND logic): both conditions must be true.
- `loop` iterates over the `users` list from `user_list.yml`. The `item` variable holds each list element.
- Developer users (tom and jake) are created on both dev AND test. Manager users (lisa) are only created on test.

---

## Task 15: Rekey an Ansible Vault File

**Points: 8**

### Step 1 - Create the initial vault file with password 'changeme01'

```bash
cd /home/vagrant/exam
ansible-vault create legacy_vault.yml
```

Enter password: `changeme01`

When the editor opens, type:

```yaml
planet: mars
```

Save and quit.

### Step 2 - Rekey the file from 'changeme01' to 'updated2024'

```bash
ansible-vault rekey legacy_vault.yml
```

When prompted:
- Vault password: `changeme01`
- New Vault password: `updated2024`
- Confirm New Vault password: `updated2024`

### Verify

```bash
ansible-vault view legacy_vault.yml
```

Enter password: `updated2024`

**Alternative one-liner for rekey:**

```bash
ansible-vault rekey --vault-password-file=<(echo 'changeme01') \
    --new-vault-password-file=<(echo 'updated2024') legacy_vault.yml
```

**Notes:**
- `ansible-vault rekey` changes the encryption password without changing the content. The file is re-encrypted with the new password.
- After rekeying, the old password (`changeme01`) no longer works.
- The file remains vault-encrypted (starts with `$ANSIBLE_VAULT`) after rekeying.
- This is a common task testing knowledge of vault password management.

---

## Task 16: Create a Cron Job

**Points: 10**

### `/home/vagrant/exam/crontab.yml`

```yaml
---
- name: Create cron job on all managed nodes
  hosts: all
  become: true

  tasks:
    - name: Create system_health_check cron job for vagrant user
      ansible.builtin.cron:
        name: "system_health_check"
        user: vagrant
        minute: "*/2"
        hour: "*"
        day: "*"
        month: "*"
        weekday: "*"
        job: 'logger "Ansible health check"'
        state: present
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook crontab.yml
```

### Verify

```bash
ansible all -m command -a 'crontab -lu vagrant'
```

**Notes:**
- `minute: "*/2"` means "every 2 minutes" (0, 2, 4, 6, ... 58).
- The `name:` parameter in `ansible.builtin.cron` is a comment label added before the cron entry. It is used by Ansible to identify and manage the specific cron job (for idempotency).
- `user: vagrant` installs the cron job in vagrant's crontab (not root's), even though `become: true` is set.
- The `job` string uses single quotes in YAML and double quotes around the logger message to ensure proper shell quoting.

---

## Task 17: Create an LVM Logical Volume

**Points: 20**

### `/home/vagrant/exam/lvm.yml`

```yaml
---
- name: Create LVM logical volume in storage_vg VG
  hosts: all
  become: true

  tasks:
    - name: Check if volume group 'storage_vg' exists
      ansible.builtin.command:
        cmd: vgdisplay storage_vg
      register: vg_check
      ignore_errors: true

    - name: Debug message when VG not found
      ansible.builtin.debug:
        msg: "VG not found"
      when: vg_check is failed

    - name: Attempt to create 500MB logical volume 'app_lv' in storage_vg VG
      ansible.builtin.lvol:
        vg: storage_vg
        lv: app_lv
        size: 500m
        state: present
      register: lv_create_500
      ignore_errors: true
      when: vg_check is succeeded

    - name: Debug message for insufficient size
      ansible.builtin.debug:
        msg: "Insufficient size of vg"
      when:
        - vg_check is succeeded
        - lv_create_500 is failed

    - name: Attempt to create 250MB logical volume 'app_lv' as fallback
      ansible.builtin.lvol:
        vg: storage_vg
        lv: app_lv
        size: 250m
        state: present
      register: lv_create_250
      ignore_errors: true
      when:
        - vg_check is succeeded
        - lv_create_500 is failed

    - name: Format logical volume with ext3 (500MB success)
      ansible.builtin.filesystem:
        fstype: ext3
        dev: /dev/storage_vg/app_lv
      when:
        - vg_check is succeeded
        - lv_create_500 is succeeded

    - name: Format logical volume with ext3 (250MB fallback success)
      ansible.builtin.filesystem:
        fstype: ext3
        dev: /dev/storage_vg/app_lv
      when:
        - vg_check is succeeded
        - lv_create_500 is failed
        - lv_create_250 is succeeded
```

### Run

```bash
cd /home/vagrant/exam
ansible-playbook lvm.yml
```

### Optional: Pre-create the storage_vg VG on a test node (if /dev/loop0 is available)

```bash
# On the managed node, as root:
sudo losetup /dev/loop0 /dev/sdb   # or use an available block device
sudo vgcreate storage_vg /dev/loop0
```

### Verify

```bash
ansible all -m command -a 'lvdisplay /dev/storage_vg/app_lv' --become
ansible all -m command -a 'blkid /dev/storage_vg/app_lv' --become
```

**Notes:**
- `vg_check is succeeded` and `vg_check is failed` use Ansible's test syntax for registered results.
- `ignore_errors: true` prevents the play from stopping when the VG does not exist or the LV creation fails.
- `ansible.builtin.lvol` requires the `lvm2` package to be installed on managed nodes.
- `ansible.builtin.filesystem` with `fstype: ext3` runs `mkfs.ext3` on the device.
- The playbook does NOT mount the LV (as specified in the task).
- On nodes where `storage_vg` VG does not exist, the playbook prints "VG not found" and skips all subsequent tasks gracefully.
- Logic flow:
  1. Check VG exists → if not, print "VG not found" and skip
  2. Try 500MB → if OK, format with ext3
  3. If 500MB fails, print "Insufficient size of vg" → try 250MB → if OK, format with ext3

---

## Quick Reference: Run All Playbooks

```bash
cd /home/vagrant/exam

# Task 2 - Repos
ansible-playbook repos.yml

# Task 5 - Apache role on dev
ansible-playbook apache_role.yml

# Task 6 - Multiple roles
ansible-playbook roles.yml

# Task 7a - Timesync
ansible-playbook timesync.yml

# Task 7b - SELinux
ansible-playbook selinux.yml

# Task 8 - Packages
ansible-playbook packages.yml

# Task 9 - Web content
ansible-playbook webcontent.yml

# Task 10 - Hardware report
ansible-playbook hwreport.yml

# Task 11 - /etc/issue
ansible-playbook issue.yml

# Task 12 - /etc/myhosts
ansible-playbook hosts.yml

# Task 14 - Users (requires vault)
ansible-playbook users.yml --vault-password-file=vault_key

# Task 16 - Cron
ansible-playbook crontab.yml

# Task 17 - LVM
ansible-playbook lvm.yml
```

## Quick Reference: Galaxy Commands

```bash
cd /home/vagrant/exam

# Install collections (Task 3)
ansible-galaxy collection install ansible.posix -p collections
ansible-galaxy collection install fedora.linux_system_roles -p collections

# Install roles from requirements (Task 4)
ansible-galaxy install -r roles/requirements.yml -p roles

# Initialize a new role skeleton (Task 5)
ansible-galaxy init roles/apache
```

## Quick Reference: Vault Commands

```bash
cd /home/vagrant/exam

# Create encrypted file (Task 13)
ansible-vault create encrypted_vars.yml --vault-password-file=vault_key

# View encrypted file
ansible-vault view encrypted_vars.yml --vault-password-file=vault_key

# Edit encrypted file
ansible-vault edit encrypted_vars.yml --vault-password-file=vault_key

# Encrypt an existing plaintext file
ansible-vault encrypt plainfile.yml --vault-password-file=vault_key

# Decrypt a vault file (makes it plaintext)
ansible-vault decrypt encrypted_vars.yml --vault-password-file=vault_key

# Rekey (change password) (Task 15)
ansible-vault rekey legacy_vault.yml
```
