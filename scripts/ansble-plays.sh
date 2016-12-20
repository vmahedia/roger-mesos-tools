#!/usr/bin/env bash

source scripts/common.sh

ansible_play(){
  local roger_ansible='roger/ansible'

  # Update kernel
  ansible-playbook   \
    -i "$HOSTS_FILE" \
    "${roger_ansible}/mesos-base.yml"

  # Restart to pickup new kernel
  vagrant reload

  # Deploy RogerOS
  ansible-playbook                         \
    "${roger_ansible}/initial-cluster.yml" \
    -i "$HOSTS_FILE"                       \
    --diff
}

restart_services(){
  # restart Zookeeper
  ansible zookeeper  \
    -i "$HOSTS_FILE" \
    -m command       \
    -a 'sudo service zookeeper restart'

  # restart mesos-master
  ansible masters    \
    -i "$HOSTS_FILE" \
    -m command       \
    -a 'sudo service mesos-master restart'

  # restart mesos-slave
  ansible slaves     \
    -i "$HOSTS_FILE" \
    -m command       \
    -a 'sudo service mesos-slave restart'

  #restart marathon
  ansible marathon_servers \
    -i "$HOSTS_FILE"       \
    -m command             \
    -a 'sudo service marathon restart'
}

main(){
  ansible_play
  restart_services
}

main
