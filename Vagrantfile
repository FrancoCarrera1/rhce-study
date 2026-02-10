# -*- mode: ruby -*-
# vi: set ft=ruby :

CONTROL_NODE = "control"
WORKERS = ["node1", "node2", "node3"]

Vagrant.configure("2") do |config|
  config.vm.box = "eurolinux-vagrant/centos-stream-9"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 1024
    vb.cpus = 1
  end

  # Ansible Control Node
  config.vm.define CONTROL_NODE, primary: true do |ctrl|
    ctrl.vm.hostname = "control.lab.local"
    ctrl.vm.network "private_network", ip: "192.168.56.10"

    ctrl.vm.provider "virtualbox" do |vb|
      vb.memory = 2048
      vb.name = "rhce-control"
    end

    ctrl.vm.provision "shell", inline: <<-SHELL
      dnf install -y epel-release
      dnf install -y ansible-core python3-pip sshpass vim
      sudo -u vagrant bash -c '
        if [ ! -f ~/.ssh/id_rsa ]; then
          ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -N ""
        fi
      '
    SHELL
  end

  # Worker Nodes (managed nodes)
  WORKERS.each_with_index do |name, index|
    config.vm.define name do |node|
      node.vm.hostname = "#{name}.lab.local"
      node.vm.network "private_network", ip: "192.168.56.#{20 + index}"

      node.vm.provider "virtualbox" do |vb|
        vb.memory = 512
        vb.name = "rhce-#{name}"
      end

      node.vm.provision "shell", inline: <<-SHELL
        dnf install -y python3
      SHELL
    end
  end
end
