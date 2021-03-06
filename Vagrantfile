# -*- mode: ruby -*-
# vi: set ft=ruby :

nodes = [
  { :hostname => 'roger-mesos-tools.local', :ip => '192.168.222.222', :mem => 2048, :cpus => 1 }
]

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provision "shell", path: "scripts/provision-vm"
  config.ssh.forward_agent = true

  if ENV['ROGER_CLI_HOST2VM_SYNCED_DIR']
    config.vm.synced_folder ENV['ROGER_CLI_HOST2VM_SYNCED_DIR'], "/home/vagrant/from_host"
  end

  # The following lines were added to support access when connected via vpn (see: http://akrabat.com/sharing-host-vpn-with-vagrant/)
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  end

  # On destroy, remove entries (if any) for the nodes in the host's ssh authorized keys
  config.trigger.after :destroy do
    run "ssh-keygen -R #{@machine.name}"
  end

  nodes.each do |entry|
    config.vm.define entry[:hostname] do |node|
      node.vm.hostname = entry[:hostname]
      node.vm.network :private_network, ip: entry[:ip]
      node.vm.provider :virtualbox do |vb|
        vb.memory = entry[:mem]
        vb.cpus = entry[:cpus]
      end
    end
  end
end
