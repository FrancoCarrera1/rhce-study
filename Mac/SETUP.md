# Lab Setup - macOS

## Prerequisites

### Intel Mac

```bash
brew install --cask virtualbox vagrant
```

### Apple Silicon (M1/M2/M3/M4)

VirtualBox has limited Apple Silicon support. Two options:

**Option A - VMware Fusion (Recommended)**

```bash
brew install --cask vmware-fusion vagrant
vagrant plugin install vagrant-vmware-desktop
```

**Option B - QEMU via libvirt**

```bash
brew install qemu libvirt vagrant
vagrant plugin install vagrant-libvirt
```

> Note: The Vagrantfile uses VirtualBox as the provider. On Apple Silicon you will
> need to override the provider when running commands:
> `vagrant up --provider=vmware_desktop` or `vagrant up --provider=libvirt`

## Setup

### 1. Reassemble the Vagrant box

The AlmaLinux 9 box is shipped as split zip parts to stay within GitHub's file size limits. Reassemble it before your first `vagrant up`:

```bash
cd Mac/
cat almalinux9-vmtools.box.zip.part_* > almalinux9-vmtools.box.zip
unzip almalinux9-vmtools.box.zip
rm almalinux9-vmtools.box.zip   # optional cleanup
```

### 2. Start the lab

```bash
vagrant up
```

## Snapshot (after first successful boot)

```bash
vagrant snapshot save clean-slate
```

## Daily Workflow

```bash
# Start VMs
vagrant up

# Reset to clean state
vagrant snapshot restore clean-slate

# SSH into nodes
vagrant ssh control
vagrant ssh node1
vagrant ssh node2
vagrant ssh node3

# Stop VMs
vagrant halt
```

## Differences from Windows Setup

- No WSL layer, Vagrant runs natively
- Synced folders work out of the box (no DrvFs issue)
- On Apple Silicon, x86_64 boxes run under emulation and will be slower
- For Apple Silicon, consider using `bento/centos-stream-9` which provides arm64 builds

## Apple Silicon Vagrantfile Override

If using VMware Fusion on Apple Silicon, add this to the Vagrantfile:

```ruby
config.vm.provider "vmware_desktop" do |v|
  v.memory = 1024
  v.cpus = 1
end
```

## Troubleshooting

- **Box not found for provider**: Make sure the box supports your provider. Use `vagrant box list` to check.
- **Slow performance on Apple Silicon**: x86_64 emulation is slow. Use arm64 boxes when available.
- **Network issues**: macOS may prompt for network extension permissions for VirtualBox/VMware. Allow them in System Settings > Privacy & Security.
