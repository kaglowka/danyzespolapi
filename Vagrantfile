# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/centos-7.5"
  config.vm.hostname = "mcod.local"
  config.vm.network "forwarded_port", guest:8000, host:8000 # mcod api
  config.vm.network "forwarded_port", guest:8080, host:8080 # mcod admin
  config.vm.network "forwarded_port", guest:8081, host:8081 # mcod frondend
  config.vm.network "forwarded_port", guest:5432, host:5432 # postgres
  config.vm.network "forwarded_port", guest:9200, host:9999 # supervisor
  config.vm.network :private_network, ip: "172.28.28.28"
  config.vm.synced_folder ".", "/vagrant"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "mcod-backend"
    vb.memory = "2048"
    vb.cpus = 2
  end

  config.vm.provision "ansible_local" do |ansible|
    ansible.provisioning_path = "/vagrant/vagrant/ansible"
    ansible.playbook = "deploy.yml"
    ansible.compatibility_mode = "2.0"
  end
end
