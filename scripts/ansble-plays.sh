#!/usr/bin/env bash

set -e -o pipefail
[ ${DEBUG:=0} -eq 1 ] && set -x

ansible_play(){
  local hosts_file=roger-mesos/vagrant/single_node/hosts/single
  echo "Kernel reload()..."
  ansible-playbook -i "$hosts_file" --user=vagrant --ask-pass roger-mesos/ansible/base.yml
  vagrant reload

  echo "Starting ansible-playbook to set up other services..."

  ansible-playbook -i "$hosts_file" --user=vagrant --ask-pass --extra-vars="mesos_cluster_name=localcluster-on-`hostname` mesos_master_network_interface=ansible_eth1 mesos_slave_network_interface=ansible_eth1" roger-mesos/ansible/initial-cluster.yml --diff -e "@roger-mesos/ansible_vars.yml"

  # restart Zookeeper
  ansible zookeeper -i "$hosts_file" --user=vagrant -s -m command -a "service zookeeper restart" --ask-pass

  # rstart mesos-master
  ansible masters -i "$hosts_file" --user=vagrant -s -m command -a "service mesos-master restart" --ask-pass

  # restart mesos-slave
  ansible slaves -i "$hosts_file" --user=vagrant -s -m command -a "service mesos-slave restart" --ask-pass

  #restart marathon
  ansible marathon_servers -i "$hosts_file" --user=vagrant -s -m command -a "service marathon restart" --ask-pass
}

main(){
  ansible_play
}

main
