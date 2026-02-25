# Lab Reference

## Lab Architecture

| Node | Hostname | IP | RAM | Role |
|------|----------|-----|-----|------|
| control | control.lab.local | 192.168.56.10 | 2GB | Ansible control node |
| node1 | node1.lab.local | 192.168.56.20 | 512MB | Managed node |
| node2 | node2.lab.local | 192.168.56.21 | 512MB | Managed node |
| node3 | node3.lab.local | 192.168.56.22 | 512MB | Managed node |

## Credentials

- **User:** `vagrant`
- **Password:** `vagrant`
- **Root password:** `vagrant`
- Vagrant user has passwordless sudo

## Daily Workflow

```powershell
# Start VMs
vagrant up

# Reset to clean state
vagrant snapshot restore clean-slate

# SSH into control node
vagrant ssh control

# SSH into worker nodes
vagrant ssh node1
vagrant ssh node2
vagrant ssh node3

# Stop VMs when done
vagrant halt
```

## Snapshot Management

```powershell
# Create snapshot (do this after initial setup)
vagrant snapshot save clean-slate

# Restore snapshot
vagrant snapshot restore clean-slate

# List snapshots
vagrant snapshot list
```

## Vagrant Commands

```powershell
# Check VM status
vagrant status

# Re-run provisioning scripts
vagrant provision

# Destroy all VMs (keeps downloaded box)
vagrant destroy -f

# Rebuild from scratch
vagrant destroy -f && vagrant up
```

## SSH Key Setup (run from control node)

```bash
# Distribute keys to worker nodes (password: vagrant)
ssh-copy-id vagrant@192.168.56.20
ssh-copy-id vagrant@192.168.56.21
ssh-copy-id vagrant@192.168.56.22

# Test connectivity
ansible all -m ping
```
